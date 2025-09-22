from __future__ import annotations

from collections import OrderedDict
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
import pandas as pd
from anndata import AnnData
from beartype import beartype
from jax import debug, lax
from numpyro.handlers import scale
from scipy import sparse

from .RNA_utils import sample_prior


@jax.jit
def mlp(params: dict[str, jnp.ndarray], x: jnp.ndarray) -> jnp.ndarray:
    """
    3-layer MLP with positive outputs:
      - Two ELU-activated hidden layers
      - Linear readout gives gene logits, then softplus ensures positivity

    params keys:
      W1: (in_dim,    H1), b1: (H1,)
      W2: (H1,       H2), b2: (H2,)
      W3: (H2, num_genes), b3: (num_genes,)
    x:       (batch_size, in_dim)
    returns: (batch_size, num_genes)
    """
    # first hidden
    h1 = jax.nn.elu(jnp.dot(x,        params["W1"]) + params["b1"])
    # second hidden
    h2 = jax.nn.elu(jnp.dot(h1,       params["W2"]) + params["b2"])
    # linear read-out
    logits = jnp.dot(h1,              params["W3"]) + params["b3"]
    # enforce non-negativity
    return jax.nn.softplus(logits)

def _linear_dt_grid(n_points: int, ratio: float) -> jnp.ndarray:
    """Return an array `t[0..n_points-1] ∈ [0,1]` where
    dt(i) grows linearly from dt_min to dt_max and dt_max/dt_min = *ratio*.
    The grid size is *n_points* (so dt array has length n_points-1).
    """
    ratio = float(max(ratio, 1.0))  # ensure ≥ 1
    N = n_points - 1  # number of intervals
    idx = jnp.arange(N, dtype=jnp.float32)
    weights = 1.0 + (ratio - 1.0) * idx / (N - 1)  # linear ramp 1 → ratio
    dt_norm = weights / weights.sum()  # normalise so Σ dt = 1
    times = jnp.concatenate([jnp.array([0.0], dtype=jnp.float32), jnp.cumsum(dt_norm)])
    return times


@beartype
def prepare_model_input(
    adata_rna: AnnData,
    tf_list: List[str],
    n_cells_col: str = "n_cells",
    prior_time_col: Optional[str] = None,
    batch_annotation: Optional[str] = None,
    prior_path_col: Optional[str] = None,
    terminal_states: Optional[List[Union[str, Tuple[str, ...]]]] = None,
    initial_states: Optional[List[Union[str, Tuple[str, ...]]]] = None,
    cluster_key: Optional[str] = None,
    prior_timespan: Optional[float] = 40,
    N_steps: int = 100,
    grid_type: str = "linear",
    grid_param: float = 1.0,
    custom_grid_fn: Optional[Callable[[int], jnp.ndarray]] = None,
) -> Dict[str, Any]:
    """
    Prepare RNA input data for the model by extracting spliced and unspliced counts,
    computing transcription factor indices, and extracting cell metadata including batch
    information from adata_rna.obs if provided.  In addition, if you supply
    `cluster_key`, `initial_states`, and `terminal_states`, this will automatically
    build a “Prior Paths” (1-based) from those labels.  If you still want to pass
    in a numeric column (`prior_path_col`) you can; that takes priority if given.

    Parameters
    ----------
    adata_rna : AnnData
        AnnData object containing RNA expression data with 'spliced' and 'unspliced' layers.
    tf_list : List[str]
        List of transcription factor names.
    n_cells_col : str, optional
        Column name in `adata_rna.obs` representing the number of cells per metacell.
    prior_time_col : Optional[str], optional
        Column name in `adata_rna.obs` containing prior pseudotimes; if provided, used
        to center the prior over t_c (default: None).
    batch_annotation : Optional[str], optional
        Column name in `adata_rna.obs` that contains batch information; if provided,
        cells are assigned batch indices based on this column.
    prior_path_col : Optional[str], optional
        (legacy) Column name in `adata_rna.obs` that contains a hard‐coded 1‐based path index;
        missing/NaN entries become −1 (inference).  Takes priority over the
        automatic cluster‐based labeling described below.
    terminal_states : Optional[List[str]], optional
        If provided (and `cluster_key` is also given), defines a list of cluster names
        that should be mapped to terminal paths.  They will be assigned raw_prior = 1..P
        in the order you list them.
    initial_states : Optional[List[str]], optional
        If provided (and `cluster_key` is also given), defines a list of cluster names
        that should be mapped to raw_prior = 0 (which then becomes prior_path = −2
        internally, i.e. “initial state”).
    cluster_key : Optional[str], optional
        Column in `adata_rna.obs` whose values are compared against `initial_states`
        or `terminal_states` to build a “Prior Path” assignment.  This is only used
        if `prior_path_col` is None.
    prior_timespan : float, optional
        Used if prior_time_col is None (default span).  Otherwise recalculated from data.
    N_steps : int, optional
        Number of grid steps (default: 100).
    grid_type : str, optional
        “linear” or “linear_dt” (default: “linear”).
    grid_param : float, optional
        Parameter for “linear_dt” spacing (ignored if grid_type=“linear”).
    custom_grid_fn : Optional[Callable[[int], jnp.ndarray]], optional
        If you want to supply your own function to build `times_norm`.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
          - `data`: JAX array of shape (cells, genes, 2) with stacked unspliced and spliced counts.
          - `M_c`: JAX array of shape (cells, 1, 1) holding the per‐cell metacell size.
          - `obs2sample`: one‐hot encoding of batch indices (shape cells × n_batch).
          - `batch_index`: JAX array of shape (cells,) with batch indices.
          - `tf_indices`: JAX array of TF gene indices.
          - `total_num_cells`: int, number of cells.
          - `n_batch`: int, number of batches.
          - `prior_time`: JAX array of prior times or None.
          - `prior_timespan`: float, span of prior_time or default.
          - `prior_path`: JAX int array of shape (cells,) with −1 or 0‐based path ids;
              prior_path = −2 means “initial state,” prior_path ≥ 0 means fixed to path id.
          - `unknown_idx`: Python list of ints, indices of cells with unknown prior (prior_path < 0).
          - `unknown_count`: int, number of unknown cells.
          - `times_norm`, `dt_norm`, `T_limits`, `hidden_units`, `num_paths`
    """

    def _to_dense_f32(layer):
        if sparse.issparse(layer):
            # cast to float32 and densify in one go
            return layer.astype(np.float32).toarray()
        else:
            # if it’s already an ndarray, just ensure dtype
            return np.asarray(layer, dtype=np.float32)

    # ========== 1) STACK RAW DATA ==========
    spliced = _to_dense_f32(adata_rna.layers["spliced"])
    unspliced = _to_dense_f32(adata_rna.layers["unspliced"])
    data = jnp.array(np.stack([unspliced, spliced], axis=-1))

    # ========== 2) METACELL SIZES ==========
    M_c = jnp.array(
        np.expand_dims(np.expand_dims(adata_rna.obs[n_cells_col].to_numpy(), -1), -1),
        dtype=jnp.float32,
    )
    total_num_cells = int(data.shape[0])

    # ========== 3) PRIOR TIME ==========
    if prior_time_col is not None:
        prior_time = jnp.array(
            adata_rna.obs[prior_time_col].to_numpy(), dtype=jnp.float32
        )
        prior_timespan = float(prior_time.max() - prior_time.min())
    else:
        prior_time = None

    # ========== 4) BATCH INDEX ==========
    if batch_annotation is not None:
        batches = adata_rna.obs[batch_annotation].astype(str)
        uniq = batches.unique()
        mapping = {b: i for i, b in enumerate(uniq)}
        batch_index = jnp.array(batches.map(mapping).to_numpy(), dtype=jnp.int32)
    else:
        batch_index = jnp.zeros(total_num_cells, dtype=jnp.int32)
    n_batch = int(jnp.unique(batch_index).shape[0])
    obs2sample = jax.nn.one_hot(batch_index, num_classes=n_batch, dtype=jnp.float32)

    # ========== 5) TF INDICES ==========
    is_tf = np.isin(adata_rna.var_names, tf_list)
    tf_indices = jnp.array(np.where(is_tf)[0], dtype=jnp.int32)
    hidden_units = int(jnp.sqrt(int(np.sum(is_tf))))

    # ========== 6) PRIOR PATH (either from prior_path_col OR from clusters) ==========
    if prior_path_col is not None:
        raw_prior = adata_rna.obs[prior_path_col].to_numpy()

    else:
        # We require cluster_key here (single column); each terminal_states entry defines one path.
        if (cluster_key is None) or (terminal_states is None):
            raise ValueError(
                "Either supply `prior_path_col`, or supply `cluster_key` and `terminal_states`."
            )

        # Initialize everything to NA (unknown)
        raw_prior = pd.Series(
            data=[pd.NA] * total_num_cells, index=adata_rna.obs.index, dtype="object"
        )

        # Helper: normalize an entry (string or tuple of strings) -> list[str]
        def _labels(entry):
            if isinstance(entry, str):
                return [entry]
            # tuple/list/set → list of strings
            try:
                return [str(x) for x in entry]
            except TypeError:
                raise TypeError(
                    "Each element of terminal_states / initial_states must be a string "
                    "or a tuple/list of strings."
                )

        # 6a) Assign initial states → raw_prior = 0 (optional)
        if initial_states is not None:
            init_mask = np.zeros(total_num_cells, dtype=bool)
            for entry in initial_states:
                labels = _labels(entry)
                init_mask |= adata_rna.obs[cluster_key].astype(str).isin(labels).to_numpy()
            raw_prior.loc[init_mask] = 0

        # 6b) Assign terminal paths → raw_prior = 1,2,… in the order given
        for idx, entry in enumerate(terminal_states, start=1):
            labels = _labels(entry)
            mask = adata_rna.obs[cluster_key].astype(str).isin(labels).to_numpy()
            # later paths override earlier ones on overlaps (explicit policy)
            raw_prior.loc[mask] = idx

        raw_prior = raw_prior.to_numpy()

    # --- Convert raw_prior (values: NA / 0 / 1..P) into model ints ---
    # num_paths = max terminal id seen (>=1); default to 1 if none
    valid_paths = [int(v) for v in raw_prior if pd.notna(v) and int(v) > 0]
    num_paths = max(valid_paths) if valid_paths else 1

    prior_path_np = np.full((total_num_cells,), -1, dtype=np.int32)  # −1 ⇒ unknown
    for i, v in enumerate(raw_prior):
        if pd.isna(v):
            continue
        v_int = int(v)
        if v_int == 0:
            prior_path_np[i] = -2        # initial state
        else:
            prior_path_np[i] = v_int - 1 # terminals 1..P → 0..P-1

    prior_path = jnp.array(prior_path_np, dtype=jnp.int32)
    unknown_idx = [int(i) for i, p in enumerate(prior_path_np) if p < 0]
    unknown_count = len(unknown_idx)

    # ========== 7) BUILD TIMEGRID ==========
    if prior_time_col is None:
        T_min = -prior_timespan / 2.0
        T_max = +prior_timespan / 2.0
    else:
        T_min = prior_time.min() - prior_timespan / 6.0
        T_max = prior_time.max() + prior_timespan / 6.0

    if grid_type == "linear":
        times_norm = jnp.linspace(0.0, 1.0, N_steps + 1)
    elif grid_type in {"linear_dt", "lin_dt"}:
        times_norm = _linear_dt_grid(N_steps + 1, ratio=float(grid_param))
    else:
        raise ValueError(f"Unknown grid_type '{grid_type}'.")

    dt_norm = jnp.diff(times_norm)  # length = N_steps

    return OrderedDict(
        [
            ("data", data),
            ("M_c", M_c),
            ("obs2sample", obs2sample),
            ("batch_index", batch_index),
            ("tf_indices", tf_indices),
            ("total_num_cells", total_num_cells),
            ("n_batch", n_batch),
            ("prior_time", prior_time),
            ("prior_timespan", prior_timespan),
            ("prior_path", prior_path),
            ("unknown_idx", unknown_idx),
            ("unknown_count", unknown_count),
            ("times_norm", times_norm),
            ("dt_norm", dt_norm),
            ("T_limits", (T_min, T_max)),
            ("hidden_units", hidden_units),
            ("num_paths", num_paths),
        ]
    )


def soft_clip(y, lower, upper, sharpness=1.0):
    y1 = lower + jax.nn.softplus(sharpness * (y - lower)) / sharpness
    y2 = upper - jax.nn.softplus(sharpness * (upper - y1)) / sharpness
    return y2

def euler_maruyama(
    times_grid: jnp.ndarray,
    dt: jnp.ndarray,
    y0: jnp.ndarray,
    drift_fn,
    diffusion_fn,
    drift_args,
    diff_args,
    eps_grid: jnp.ndarray,
) -> jnp.ndarray:
    """
    Perform Euler–Maruyama integration on a fixed time grid for multiple sample paths.

    Parameters:
    - times_grid (jnp.ndarray): 1D array of time points of length L.
    - dt (jnp.ndarray): 1D array of time step sizes between grid points, length L-1.
    - y0 (jnp.ndarray): Initial state for each path, shape (num_paths, num_genes, 3).
    - drift_fn (Callable): Function computing deterministic drift: f = drift_fn(t, y, drift_args).
    - diffusion_fn (Callable): Function computing stochastic diffusion: g = diffusion_fn(t, y, diff_args).
    - drift_args (Any): Extra arguments to pass to drift_fn.
    - diff_args (Any): Extra arguments to pass to diffusion_fn.
    - eps_grid (jnp.ndarray): Pre-sampled Gaussian noise, shape (num_paths, L-1, num_genes).

    Returns:
    - jnp.ndarray: Simulated state trajectory, shape (L, num_paths, num_genes, 3).
    """
    eps = jnp.swapaxes(eps_grid, 0, 1)

    def body_fn(carry, inputs):
        y_prev, t_prev = carry
        eps_i, dt_i = inputs
        f = drift_fn(t_prev, y_prev, drift_args) * dt_i
        g = diffusion_fn(t_prev, y_prev, diff_args)
        st = g * (jnp.sqrt(dt_i)[None, None, None] * eps_i[..., None])
        y_new = y_prev + f + st
        y_new = jnp.clip(y_new, 0.0, 1000)
        return (y_new, t_prev + dt_i), y_new

    (y_last, _), ys = jax.lax.scan(body_fn, (y0, times_grid[0]), (eps, dt))
    return jnp.concatenate([y0[None], ys], axis=0)


@jax.jit
def interpolate_solution(
    sol_grid: jnp.ndarray,
    times_grid: jnp.ndarray,
    T_c: jnp.ndarray,
) -> jnp.ndarray:
    """
    Linearly interpolate a precomputed solution grid at specified cell times.

    Parameters:
    - sol_grid (jnp.ndarray): Solution values on a regular time grid, shape (L, num_paths, num_genes, 3).
    - times_grid (jnp.ndarray): 1D array of time points corresponding to sol_grid, length L.
    - T_c (jnp.ndarray): Array of arbitrary times at which to interpolate, shape (num_cells,).

    Returns:
    - jnp.ndarray: Interpolated solution at each time in T_c, shape (num_cells, num_paths, num_genes, 3).
    """
    idx0 = jnp.searchsorted(times_grid, T_c, side="right") - 1
    idx0 = jnp.clip(idx0, 0, sol_grid.shape[0] - 2)
    t0 = times_grid[idx0]
    t1 = times_grid[idx0 + 1]
    sol0 = sol_grid[idx0]
    sol1 = sol_grid[idx0 + 1]
    w = ((T_c - t0) / (t1 - t0))[..., None, None, None]
    return sol0 * (1 - w) + sol1 * w


@jax.jit
def diffusion_fn(t, y, diff_args):
    """
    Compute the diffusion term for the SDE, nonzero only on the protein dimension
    for specified transcription factor genes.

    Parameters:
    - t (float): Current time.
    - y (jnp.ndarray): Current state array, shape (num_paths, num_genes, 3).
    - diff_args (tuple): Tuple containing:
        - sigma_tf (jnp.ndarray): Diffusion strengths for each TF, shape (num_tfs,).
        - tf_indices (array-like): Indices of transcription factor genes.

    Returns:
    - jnp.ndarray: Diffusion contribution, same shape as y.
    """
    sigma_tf, tf_indices = diff_args
    return jnp.zeros_like(y).at[:, tf_indices, 2].set(sigma_tf[None, :])


@jax.jit
def drift_fn(t, state, args):
    """
    Compute the deterministic drift for the coupled transcription–splicing–protein system.

    Parameters:
    - t (float): Current time.
    - state (jnp.ndarray): Current state, shape (num_paths, num_genes, 3), containing
      unspliced (u), spliced (s), and protein (p) counts.
    - args (tuple): Tuple containing:
        - alpha_0 (jnp.ndarray): Baseline transcription rates, shape (num_genes,).
        - beta_g (jnp.ndarray): Splicing rates per gene, shape (num_genes,).
        - gamma_g (jnp.ndarray): Degradation rates per gene, shape (num_genes,).
        - lamda (jnp.ndarray): Translation rates for TF proteins, shape (num_tfs,).
        - kappa (jnp.ndarray): Protein degradation rates for TFs, shape (num_tfs,).
        - nn_params (dict): Neural network parameters for computing regulation.
        - tf_indices (array-like): Indices of transcription factor genes.
        - T_ON (float): Switch-on time threshold.

    Returns:
    - jnp.ndarray: Time derivative of the state, same shape as state.
    """
    alpha_0, beta_g, gamma_g, lamda, kappa, nn_params, tf_indices = args

    u = jnp.clip(state[..., 0], 0, 10 ** (3))
    s = jnp.clip(state[..., 1], 0, 10 ** (3))
    p = jnp.clip(state[..., 2], 0, 10 ** (3))

    alpha = alpha_0 * jnp.clip(mlp(nn_params, p[:, tf_indices]), 0, 10 ** (3))
    du_dt = alpha - beta_g * u
    ds_dt = beta_g * u - gamma_g * s

    dp_dt = jnp.zeros_like(u)
    dp_dt = dp_dt.at[:, tf_indices].set(
        lamda * s[:, tf_indices] - kappa * p[:, tf_indices]
    )

    return jnp.stack([du_dt, ds_dt, dp_dt], axis=-1)

# Define the complete NumPyro model
def model(
    data: Any,
    M_c: Any,
    obs2sample: Any,
    batch_index: Any,
    tf_indices: Any,
    total_num_cells: int,
    n_batch: int,
    prior_time: Any,
    prior_timespan: Any,
    prior_path: Any,
    unknown_idx: Any,
    unknown_count: int,
    times_norm: Any,
    dt_norm: Any,
    T_limits: Any,
    hidden_units: int,
    num_paths: int,
    return_alpha: bool = False,
    Tmax_alpha: float = 50.0,
    Tmax_beta: float = 1.0,
    splicing_rate_alpha_hyp_prior_alpha: float = 20.0,
    splicing_rate_alpha_hyp_prior_mean: float = 5.0,
    splicing_rate_mean_hyp_prior_alpha: float = 10.0,
    splicing_rate_mean_hyp_prior_mean: float = 1.0,
    degradation_rate_alpha_hyp_prior_alpha: float = 20.0,
    degradation_rate_alpha_hyp_prior_mean: float = 5.0,
    degradation_rate_mean_hyp_prior_alpha: float = 10.0,
    degradation_rate_mean_hyp_prior_mean: float = 1.0,
    transcription_rate_alpha_hyp_prior_alpha: float = 20.0,
    transcription_rate_alpha_hyp_prior_mean: float = 2.0,
    transcription_rate_mean_hyp_prior_alpha: float = 10.0,
    transcription_rate_mean_hyp_prior_mean: float = 5.0,
    lambda_alpha: float = 1.0,
    lambda_mean: float = 1.0,
    kappa_alpha: float = 1.0,
    kappa_mean: float = 1.0,
    detection_mean_hyp_prior_alpha: float = 1.0,
    detection_mean_hyp_prior_beta: float = 1.0,
    detection_hyp_prior_alpha: float = 10.0,
    detection_i_prior_alpha: float = 100.0,
    detection_gi_prior_alpha: float = 200.0,
    gene_add_alpha_hyp_prior_alpha: float = 9.0,
    gene_add_alpha_hyp_prior_beta: float = 3.0,
    gene_add_mean_hyp_prior_alpha: float = 1.0,
    gene_add_mean_hyp_prior_beta: float = 100.0,
    stochastic_v_ag_hyp_prior_alpha: float = 9.0,
    stochastic_v_ag_hyp_prior_beta: float = 3.0,
    init_seed: int = 0,
    **kwargs
):
    """
    NumPyro model for coupled transcription and splicing dynamics.

    Args:
        data: Observed data array of shape (num_cells, num_genes, num_modalities).
        M_c: Number of cells in each metacell.
        batch_index: Array indicating batch assignments for each cell.
        tf_indices: Indices of genes that are TFs.
        total_num_cells: Number of cells in the full dataset.
        n_batch: Number of batches.
        Tmax_alpha: Alpha parameter for Tmax prior.
        Tmax_beta: Beta parameter for Tmax prior.
        ... (other hyperparameters for priors)
        key: Random number generator key.

    Returns:
        None. Defines the probabilistic model for inference.
    """

    num_cells = int(data.shape[0])
    num_genes = int(data.shape[1])
    num_modalities = int(data.shape[2])
    num_tfs = int(tf_indices.shape[0])
    batch_size = num_cells
    n_keys = 3
    base_key = jax.random.PRNGKey(init_seed)
    all_keys = jax.random.split(base_key, n_keys)

    # Splicing Rates for mRNA
    splicing_alpha = numpyro.sample(
        "splicing_alpha",
        dist.Gamma(
            splicing_rate_alpha_hyp_prior_alpha,
            splicing_rate_alpha_hyp_prior_alpha / splicing_rate_alpha_hyp_prior_mean,
            validate_args=True,
        ),
    )
    splicing_alpha = jnp.clip(splicing_alpha, a_min=1e-2, a_max=1e3)

    splicing_mean = numpyro.sample(
        "splicing_mean",
        dist.Gamma(
            splicing_rate_mean_hyp_prior_alpha,
            splicing_rate_mean_hyp_prior_alpha / splicing_rate_mean_hyp_prior_mean,
            validate_args=True,
        ),
    )
    splicing_mean = jnp.clip(splicing_mean, a_min=1e-2, a_max=1e3)

    beta_g = numpyro.sample(
        "beta_g",
        dist.Gamma(splicing_alpha, splicing_alpha / splicing_mean, validate_args=True)
        .expand([num_genes])
        .to_event(1),
    )

    # Degradation Rates for mRNA
    degradation_alpha = numpyro.sample(
        "degradation_alpha",
        dist.Gamma(
            degradation_rate_alpha_hyp_prior_alpha,
            degradation_rate_alpha_hyp_prior_alpha
            / degradation_rate_alpha_hyp_prior_mean,
            validate_args=True,
        ),
    )
    degradation_alpha = degradation_alpha + 0.001  # Prevent zero

    degradation_mean = numpyro.sample(
        "degradation_mean",
        dist.Gamma(
            degradation_rate_mean_hyp_prior_alpha,
            degradation_rate_mean_hyp_prior_alpha
            / degradation_rate_mean_hyp_prior_mean,
            validate_args=True,
        ),
    )
    degradation_mean = jnp.clip(degradation_mean, a_min=1e-2, a_max=1e3)

    gamma_g = numpyro.sample(
        "gamma_g",
        dist.Gamma(
            degradation_alpha, degradation_alpha / degradation_mean, validate_args=True
        )
        .expand([num_genes])
        .to_event(1),
    )

    # Translation rate for proteins
    lamda = numpyro.sample(
        "lambda",
        dist.Gamma(lambda_alpha, lambda_alpha / lambda_mean, validate_args=True)
        .expand([num_tfs])
        .to_event(1),
    )
    # Degradation rate for proteins
    kappa = numpyro.sample(
        "kappa",
        dist.Gamma(kappa_alpha, kappa_alpha / kappa_mean, validate_args=True)
        .expand([num_tfs])
        .to_event(1),
    )

    # Time Parameters
    # 1) sample a *single* global scaling factor
    T_min, T_max = T_limits
    T_scaling = numpyro.sample("T_scaling", dist.Beta(1.0, 3.0))
    total_span = (T_max - T_min) * T_scaling

    # 2) build *static‐shape* grid (always N_steps long)
    times_grid = T_min * T_scaling + times_norm * total_span
    dt = dt_norm * total_span

    # convert your absolute prior_time (if any) into a [0,1] loc/scale
    if prior_time is None:
        prior_time = T_min + (T_max - T_min) / 2
        prior_time_sd = prior_timespan / 2.0
    else:
        prior_time_sd = prior_timespan / 6.0

    with numpyro.plate("cells", batch_size):
        t_c = numpyro.sample(
            "t_c",
            dist.TruncatedNormal(
                loc=prior_time,
                scale=prior_time_sd,
                low=T_limits[0],
                high=T_limits[1],
            ),
        )
        T_c = numpyro.deterministic("T_c", T_scaling * t_c)

    # ─── 2) Sample one pulse‐center T_p per path ───────────────────────
    with numpyro.plate("paths", num_paths):
        t_p = numpyro.sample(
            "t_p",
            dist.TruncatedNormal(
                loc=(T_limits[0] + T_limits[1]) / 4,
                scale=(T_limits[1] - T_limits[0]) / 8,
                low=T_limits[0],
                high=T_limits[1],
            ),
        )  # shape = (num_paths,)

    T_p = numpyro.deterministic("T_p", T_scaling * t_p)

    # ─── 3) (Optionally) sample a width for all pulses ─────────────────
    width = 0.025 * total_span #numpyro.sample("pulse_width", dist.HalfNormal(total_span/200.0))

    # ============= Expression model =============== #

    # scale of alpha
    alpha_0 = numpyro.sample(
        "alpha_0",
        dist.Gamma(1.0, 1.0, validate_args=True).expand([num_genes]).to_event(1),
    )

    # Initial Conditions for ODE, sampling only for spliced and unspliced
    initial_state_2d = numpyro.sample(
        "initial_state_2d",
        dist.Gamma(1.0, 1.0/0.1, validate_args=True).expand([1, num_genes, 2]).to_event(1),
    )

    # Create the third dimension containing proteins, only for TFs:
    third_dimension = jnp.zeros((1, num_genes))
    third_dimension = third_dimension.at[0, tf_indices].set(
        numpyro.sample(
            "initial_state_tf",
            dist.Gamma(1.0, 1.0/0.1, validate_args=True).expand([len(tf_indices)]),
        )
    )

    # Concatenate the dimensions to form the final initial state
    initial_state = jnp.concatenate(
        [initial_state_2d, third_dimension[..., None]], axis=-1
    )

    # Neural Net params
    H = hidden_units
    W1 = numpyro.param(
        "W1", jax.random.normal(all_keys[0], (tf_indices.shape[0], H)) * 0.01
    )
    b1 = numpyro.param("b1", jnp.zeros((H,)))
    W2 = numpyro.param(
        "W2", jax.random.normal(all_keys[1], (H, H)) * 0.01
    )
    b2 = numpyro.param("b2", jnp.zeros((H,)))
    W3 = numpyro.param(
        "W3", jax.random.normal(all_keys[2], (H, data.shape[1])) * 0.01
    )
    b3 = numpyro.param("b3", jnp.zeros((data.shape[1],)))
    nn_params = {"W1": W1, "b1": b1, "W2": W2, "b2": b2, "W3": W3, "b3": b3}

    # # ---- hierarchical log-σ prior --------------------
    log_tau   = numpyro.sample("log_tau_sigma", dist.Normal(jnp.log(0.1), 0.1))
    log_lam   = numpyro.sample(
        "log_lam_sigma",
        dist.Normal(0.0, 1.0).expand([num_tfs]).to_event(1)
    )
    sigma_tf  = jnp.exp(log_tau + log_lam)

    # 2) Path-specific direction vector ε (in [–1,1]):
    with numpyro.plate("paths", num_paths):
        eps_sign = numpyro.sample(
          "eps_sign",
          dist.Uniform(-1.0, 1.0)
              .expand([num_tfs])
              .to_event(1)
        )  # shape = (num_paths, num_tfs)

    ode_args = (alpha_0, beta_g, gamma_g, lamda, kappa, nn_params, tf_indices)
    diff_args = (sigma_tf, tf_indices)

    # ───────── Build three masks ─────────
    known_mask = prior_path >= 0  # fixed-path cells
    initial_mask = prior_path == -2  # “initial-state” cells

    one_hot_known = jax.nn.one_hot(jnp.clip(prior_path, 0, num_paths - 1), num_paths)

    # ───────── Hyperparameters for Logistic-Normal ─────────
    sigma_init = 0.005
    sigma_unknown = 1.0

    sigma_matrix = jnp.where(
        initial_mask[:, None],
        jnp.ones((1, num_paths)) * sigma_init,
        jnp.ones((1, num_paths)) * sigma_unknown,
    )

    with numpyro.plate("cells", batch_size):
        z_pw = numpyro.sample(
            "z_pw",
            dist.Normal(loc=jnp.zeros((1, num_paths)), scale=sigma_matrix).to_event(1),
        )

    w_full = jax.nn.softmax(z_pw, axis=-1)  # (n_cells, num_paths)
    w_final = jnp.where(known_mask[:, None], one_hot_known, w_full)

    path_weights = numpyro.deterministic("path_weights", w_final)

    # 5) Build sched of shape (paths, L-1):
    sched = jnp.exp(
      -0.5 * ((times_grid[None, :-1] - T_p[:, None]) / (width)) ** 2
    )

    eps_tf = numpyro.deterministic(
        "eps_tf", sched[:, :, None] * eps_sign[:, None, :])

    # 4) scatter into full genes:
    eps_grid = jnp.zeros((num_paths, dt.shape[0], num_genes))
    eps_grid = eps_grid.at[:, :, tf_indices].set(eps_tf)

    # integrate once on the grid
    sol_grid = euler_maruyama(
        times_grid,
        dt,
        jnp.tile(initial_state, (num_paths, 1, 1)),
        drift_fn,
        diffusion_fn,
        ode_args,
        diff_args,
        eps_grid,
    )

    # # Smoothness penalty:
    d1 = sol_grid[1:] - sol_grid[:-1]
    d2 = d1[1:] - d1[:-1]
    penalty = jnp.sum(jnp.square(d2))/times_norm.shape[0]
    numpyro.factor("smoothness_penalty", - 10**6 * penalty)

    # interpolate each cell at its own time T_c
    sol_at_cells = numpyro.deterministic(
        "sol_at_cells", interpolate_solution(sol_grid, times_grid, T_c)
    )

    # weighted average over paths
    weighted_preds = numpyro.deterministic(
        "predictions_rearranged",
        jnp.sum(sol_at_cells * path_weights[:, :, None, None], axis=1),
    )

    # use weighted_preds[..., :2] as mu_expression downstream
    mu_expression = jnp.clip(weighted_preds[..., :2], a_min=1e-5, a_max=1e5)

    if return_alpha:

        # 1) Extract full protein at each grid point:
        P_full = sol_grid[..., 2]  # shape = (L, P, G)

        # 2) Compute “protein before the noise” for each step t=1..L-1:
        # t_vec has shape (L-1,) and sol_grid[:-1] has shape (L-1, P, G, 3).
        dp_dt_full = jax.vmap(
            lambda t, y: drift_fn(t, y, ode_args),
            in_axes=(0, 0)
        )(times_grid[:-1], sol_grid[:-1])  # → shape (L-1, P, G, 3)
        dp_dt_grid = dp_dt_full[..., 2]  # shape (L-1, P, G)

        det_increment = dp_dt_grid * dt[:, None, None]
        P_before_noise = sol_grid[:-1, ..., 2] + det_increment                     # (L-1, P, G)

        # 3) Select TF‐protein columns and flatten to feed into mlp:
        tf_prot_full   = P_full[1:, :, tf_indices]         # (L-1, P, num_tfs)
        tf_prot_before = P_before_noise[:, :, tf_indices]  # (L-1, P, num_tfs)
        flat_full      = tf_prot_full.reshape(-1, len(tf_indices))    # ((L-1)*P, num_tfs)
        flat_before    = tf_prot_before.reshape(-1, len(tf_indices))  # ((L-1)*P, num_tfs)

        # 4) Compute α for each gene at each (t, p):
        out_full_flat   = mlp(nn_params, flat_full)    # ((L-1)*P, num_genes)
        out_before_flat = mlp(nn_params, flat_before)  # ((L-1)*P, num_genes)

        # multiply by alpha_0 and reshape to (L-1, P, G)
        alpha_full = (alpha_0 * out_full_flat).reshape(tf_prot_full.shape[0],
                                                       tf_prot_full.shape[1],
                                                       alpha_0.shape[0])
        alpha_before = (alpha_0 * out_before_flat).reshape(tf_prot_before.shape[0],
                                                           tf_prot_before.shape[1],
                                                           alpha_0.shape[0])

        numpyro.deterministic("alpha_full_grid",   alpha_full)   # (L-1, P, G)
        numpyro.deterministic("alpha_before_grid", alpha_before) # (L-1, P, G)

    # ───── Measurement noise ─────

    detection_mean_y_e = numpyro.sample(
        "detection_mean_y_e",
        dist.Beta(
            jnp.ones((1, 1)) * detection_mean_hyp_prior_alpha,
            jnp.ones((1, 1)) * detection_mean_hyp_prior_beta,
            validate_args=True,
        )
        .expand([n_batch, 1])
        .to_event(2),
    )

    beta = ((detection_hyp_prior_alpha / (obs2sample @ detection_mean_y_e)).T)[0, ...]

    with numpyro.plate("cells", batch_size):
        detection_y_c = numpyro.sample(
            "detection_y_c", dist.Gamma(detection_hyp_prior_alpha, beta)
        )

    detection_y_i = numpyro.sample(
        "detection_y_i",
        dist.Gamma(detection_i_prior_alpha, detection_i_prior_alpha, validate_args=True)
        .expand([1, 1, 2])
        .to_event(3),
    )

    detection_y_gi = numpyro.sample(
        "detection_y_gi",
        dist.Gamma(
            jnp.ones((1, 1)) * detection_gi_prior_alpha,
            jnp.ones((1, 1)) * detection_gi_prior_alpha,
            validate_args=True,
        )
        .expand([1, num_genes, 2])
        .to_event(3),
    )

    # ======= Gene-specific additive component (Ambient RNA/ "Soup") for spliced and unspliced counts ====== #

    s_g_gene_add_alpha_hyp = numpyro.sample(
        "s_g_gene_add_alpha_hyp",
        dist.Gamma(
            gene_add_alpha_hyp_prior_alpha,
            gene_add_alpha_hyp_prior_beta,
            validate_args=True,
        ),
        sample_shape=(2,),
    )

    s_g_gene_add_mean = numpyro.sample(
        "s_g_gene_add_mean",
        dist.Gamma(
            gene_add_mean_hyp_prior_alpha,
            gene_add_mean_hyp_prior_beta,
            validate_args=True,
        )
        .expand([n_batch, 1, 2])
        .to_event(3),
    )

    s_g_gene_add_alpha_e_inv = numpyro.sample(
        "s_g_gene_add_alpha_e_inv",
        dist.Exponential(s_g_gene_add_alpha_hyp).expand([n_batch, 1, 2]).to_event(3),
    )

    s_g_gene_add_alpha_e = jnp.ones((1, 1)) / s_g_gene_add_alpha_e_inv**2

    s_g_gene_add = numpyro.sample(
        "s_g_gene_add",
        dist.Gamma(
            s_g_gene_add_alpha_e,
            s_g_gene_add_alpha_e / s_g_gene_add_mean,
            validate_args=True,
        )
        .expand([n_batch, num_genes, 2])
        .to_event(3),
    )

    # ========= Gene-specific overdispersion of spliced and unspliced counts ============== #

    stochastic_v_ag_hyp = numpyro.sample(
        "stochastic_v_ag_hyp",
        dist.Gamma(
            stochastic_v_ag_hyp_prior_alpha,
            stochastic_v_ag_hyp_prior_beta,
            validate_args=True,
        )
        .expand([1, 2])
        .to_event(2),
    )

    stochastic_v_ag_inv = numpyro.sample(
        "stochastic_v_ag_inv",
        dist.Exponential(stochastic_v_ag_hyp).expand([1, num_genes, 2]).to_event(3),
    )

    stochastic_v_ag = jnp.ones((1, 1)) / stochastic_v_ag_inv**2

    # ===================== Expected expression ======================= #

    additive_term = numpyro.deterministic(
        "additive_term", jnp.einsum("cb,bgi->cgi", obs2sample, s_g_gene_add)
    )

    normalizing_term = numpyro.deterministic(
        "normalizing_term",
        detection_y_c[:, None, None] * detection_y_i * detection_y_gi * M_c,
    )

    mu = numpyro.deterministic("mu", (mu_expression + additive_term) * normalizing_term)

    # Data likelihood
    concentration = stochastic_v_ag * M_c
    rate = concentration / mu
    scale_factor = total_num_cells / batch_size
    with scale(scale=scale_factor):
        numpyro.sample("data_target", dist.GammaPoisson(concentration, rate), obs=data)

# ============================
# GRN Linearization Utilities
# ============================

def _maybe_get_cell_indices(posterior):
    for where in ("means", "samples", "params", None):
        container = posterior if where is None else posterior.get(where, {})
        if isinstance(container, dict) and "cell_indices" in container:
            idx = np.array(container["cell_indices"])
            if idx.ndim > 1:
                idx = idx[0]
            return idx.astype(int)
    return None

def _get_posterior_array(posterior, name, reduce_samples=True):
    """
    Robustly fetch a site/param from posterior containers.
    Priority: means -> params -> samples -> top-level.
    If coming from 'samples' and reduce_samples=True, returns the mean over the first axis.
    """
    if isinstance(posterior, dict):
        if "means" in posterior and name in posterior["means"]:
            return jnp.array(posterior["means"][name])
        if "params" in posterior and name in posterior["params"]:
            return jnp.array(posterior["params"][name])
        if "samples" in posterior and name in posterior["samples"]:
            arr = posterior["samples"][name]
            arr = jnp.array(arr)
            return arr.mean(axis=0) if (reduce_samples and arr.ndim >= 1) else arr
        if "deterministic" in posterior and name in posterior["deterministic"]:
            arr = posterior["deterministic"][name]
            arr = jnp.array(arr)
            return arr.mean(axis=0) if (reduce_samples and arr.ndim >= 1) else arr
        if name in posterior:
            return jnp.array(posterior[name])
    raise KeyError(f"Could not find '{name}' in posterior (checked means, params, samples, top-level).")

# ---- 3-layer MLP pieces (elu -> elu -> linear -> softplus) ----
def _mlp_hidden1(ptf, W1, b1):
    return jax.nn.elu(jnp.dot(ptf, W1) + b1)

def _mlp_hidden2(ptf, W1, b1, W2, b2):
    h1 = _mlp_hidden1(ptf, W1, b1)
    return jax.nn.elu(jnp.dot(h1, W2) + b2)

def _mlp_logits(ptf, W1, b1, W2, b2, W3, b3):
    h2 = _mlp_hidden2(ptf, W1, b1, W2, b2)
    return jnp.dot(h2, W3) + b3

def _mlp_reg(ptf, W1, b1, W2, b2, W3, b3):
    return jax.nn.softplus(_mlp_logits(ptf, W1, b1, W2, b2, W3, b3))

# ---- core linearization ----
def linearize_grn_at_p(p_ref, *, tf_indices, nn_params, alpha_0):
    W1, b1 = nn_params["W1"], nn_params["b1"]
    W2, b2 = nn_params["W2"], nn_params["b2"]
    W3, b3 = nn_params["W3"], nn_params["b3"]

    ptf_ref = p_ref[tf_indices]

    f_h1     = lambda ptf: _mlp_hidden1(ptf, W1, b1)
    f_h2     = lambda ptf: _mlp_hidden2(ptf, W1, b1, W2, b2)
    f_logits = lambda ptf: _mlp_logits(ptf, W1, b1, W2, b2, W3, b3)
    f_reg    = lambda ptf: _mlp_reg(ptf, W1, b1, W2, b2, W3, b3)
    f_alpha  = lambda ptf: alpha_0 * f_reg(ptf)

    return {
        "h1_ref":         f_h1(ptf_ref),
        "h2_ref":         f_h2(ptf_ref),
        "logits_ref":     f_logits(ptf_ref),
        "reg_ref":        f_reg(ptf_ref),
        "alpha_ref":      f_alpha(ptf_ref),
        "ptf_ref":        ptf_ref,
        "J_tf_to_h1":     jax.jacfwd(f_h1)(ptf_ref),
        "J_tf_to_h2":     jax.jacfwd(f_h2)(ptf_ref),
        "J_tf_to_logits": jax.jacfwd(f_logits)(ptf_ref),
        "J_tf_to_reg":    jax.jacfwd(f_reg)(ptf_ref),
        "J_tf_to_alpha":  jax.jacfwd(f_alpha)(ptf_ref),
    }

def linearize_grn_batched(p_refs, *, tf_indices, nn_params, alpha_0):
    outs = [linearize_grn_at_p(p_refs[i], tf_indices=tf_indices,
                               nn_params=nn_params, alpha_0=alpha_0)
            for i in range(p_refs.shape[0])]
    keys = outs[0].keys()
    return {k: jnp.stack([o[k] for o in outs], axis=0) for k in keys}

def _extract_proteins_from_posterior(posterior):
    sol = _get_posterior_array(posterior, "predictions_rearranged")
    if sol.ndim == 3:
        return jnp.array(sol[..., 2])       # (cells, G)
    elif sol.ndim == 4:
        return jnp.array(sol[:, 0, :, 2])   # fallback: take path 0
    else:
        raise ValueError(f"Unexpected ndim {sol.ndim} for predictions_rearranged")

def linearize_per_celltype(adata_rna, posterior, model_input, *, cell_type_key="RNA_cell_type"):
    mu_protein = _extract_proteins_from_posterior(posterior)
    ct_full = adata_rna.obs[cell_type_key].astype(str).to_numpy()
    cell_idx = _maybe_get_cell_indices(posterior)
    ct_col = ct_full[cell_idx] if cell_idx is not None else ct_full
    if mu_protein.shape[0] != ct_col.shape[0]:
        raise ValueError("Mismatch between predictions_rearranged cells and adata cells.")

    # average protein per cell type
    unique_ct, p_refs, labels = np.unique(ct_col), [], []
    for ct in unique_ct:
        mask = (ct_col == ct)
        p_refs.append(mu_protein[np.where(mask)[0]].mean(axis=0))
        labels.append(ct)
    p_refs = jnp.stack([jnp.array(x) for x in p_refs], axis=0)
    labels = np.array(labels)

    # collect params
    W1 = _get_posterior_array(posterior, "W1")
    b1 = _get_posterior_array(posterior, "b1")
    W2 = _get_posterior_array(posterior, "W2")
    b2 = _get_posterior_array(posterior, "b2")
    W3 = _get_posterior_array(posterior, "W3")
    b3 = _get_posterior_array(posterior, "b3")
    alpha_0 = _get_posterior_array(posterior, "alpha_0")
    nn_params = {"W1": W1, "b1": b1, "W2": W2, "b2": b2, "W3": W3, "b3": b3}

    lin_batch = linearize_grn_batched(
        p_refs, tf_indices=model_input["tf_indices"],
        nn_params=nn_params, alpha_0=alpha_0
    )
    return lin_batch, labels
