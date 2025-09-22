from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
import pandas as pd
from anndata import AnnData
from beartype import beartype
from jax import jacfwd, lax
from numpyro.distributions import constraints
from numpyro.handlers import scale
from scipy import sparse

from .RNA_utils import sample_prior


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
    prior_timespan: Optional[float] = 40,
    N_steps: int = 100,
    grid_type: str = "linear",
    grid_param: float = 1.0,
    custom_grid_fn: Optional[Callable[[int], jnp.ndarray]] = None,
):
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
            ("times_norm", times_norm),
            ("T_limits", (T_min, T_max)),
            ("hidden_units", hidden_units),
        ],
    )

def soft_clip(y, lower, upper, sharpness=1.0):
    y1 = lower + jax.nn.softplus(sharpness * (y - lower)) / sharpness
    y2 = upper - jax.nn.softplus(sharpness * (upper - y1)) / sharpness
    return y2

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
def hill_regulation(p_tf: jnp.ndarray, params: dict[str, jnp.ndarray]) -> jnp.ndarray:
    """
    Interpretable 2-layer MLP with positive outputs:
      - Hidden modules use ReLU thresholding
      - Linear readout gives gene logits, then softplus ensures positivity

    Args:
        params: dict with 'W1','b1','W2','b2'.
        x:      Array (batch_size, num_tfs) of TF levels.

    Returns:
        Array (batch_size, num_genes) of non-negative transcription rates.
    """

    # Module activations (logical combination of TFs)
    h = jax.nn.elu(jnp.dot(p_tf, params["W1"]) + params["b1"])
    # Linear read-out to genes
    logits = jnp.dot(h, params["W2"]) + params["b2"]
    # Enforce non-negativity: softplus activation
    out = jax.nn.softplus(logits)
    return out

# Define the ODE function using the MLP
@beartype
def dstate_dt(t, state, args):
    """
    Compute the derivative of the state vector for the coupled system using a neural network.

    Args:
        t: Time scalar.
        state: State vector [u_1, ..., u_G, s_1, ..., s_G].
        args: Tuple containing parameters (G, beta_g, gamma_g, nn_params, T_ON).

    Returns:
        Derivative of the state vector
    """

    alpha_0, beta_g, gamma_g, lamda, kappa, hill_params, tf_indices = args
    u = state[..., 0]  # Unspliced counts for all genes.
    s = state[..., 1]  # Spliced counts for all genes.
    p = state[..., 2]  # Proteins for all genes.

    # Clip state values to increase numerical stability:
    u = jnp.clip(u, 0, 1e3)
    s = jnp.clip(s, 0, 1e3)
    p = jnp.clip(p, 0, 1e3)

    # Compute transcription rates using the neural network
    p_tf = p[:, tf_indices]   # (batch, num_tfs)

    reg = hill_regulation(
        p_tf,
        hill_params
    )

    alpha = jnp.clip(alpha_0 * reg, 0.0, 1e3)

    du_dt = alpha - beta_g * u
    ds_dt = beta_g * u - gamma_g * s
    # Compute dp_dt only for TF indices
    dp_dt = jnp.zeros_like(u)
    dp_dt = dp_dt.at[:, tf_indices].set(
        lamda * s[:, tf_indices] - kappa * p[:, tf_indices]
    )

    dstate_dt = jnp.stack([du_dt, ds_dt, dp_dt], axis=-1)  # Shape: (3G,)
    return dstate_dt

def euler_integrator(
    times: jnp.ndarray,      # (L+1,)
    y0: jnp.ndarray,         # state at t0, shape (G,3)
    drift_fn: Any,           # f(t, y, args) -> dy/dt
    drift_args: Any,
    rng_key: jax.random.PRNGKey,
    sigma_noise: float = 1e-4,   # ← small noise scale
) -> jnp.ndarray:
    """
    Euler–Maruyama integrator: y_{n+1} = y_n + f(t_n,y_n)*dt + sigma_noise*sqrt(dt)*eps_n
    """
    dt = jnp.diff(times)  # (L,)
    # draw one Gaussian noise array per step
    eps = jax.random.normal(rng_key, shape=(dt.shape[0],) + y0.shape)  # (L, G, 3)

    def step(carry, inp):
        y_prev, t_prev = carry
        dt_i, eps_i = inp
        f      = drift_fn(t_prev, y_prev, drift_args)
        # scale the noise by sqrt(dt_i)
        noise  = sigma_noise * jnp.sqrt(dt_i)[None, None] * eps_i
        y_new  = y_prev + f * dt_i + noise
        # optional clipping for stability
        y_new  = jnp.clip(y_new, 0.0, 1e3)
        return (y_new, t_prev + dt_i), y_new

    (final, _), ys = lax.scan(step, (y0, times[0]), (dt, eps))
    return jnp.concatenate([y0[None], ys], axis=0)

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
    times_norm: Any,
    T_limits: Any,
    hidden_units: Any,
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
    lambda_alpha: float = 10.0,
    lambda_mean: float = 20.0,
    kappa_alpha: float = 1.0,
    kappa_mean: float = 2.0,
    detection_mean_hyp_prior_alpha: float = 1.0,
    detection_mean_hyp_prior_beta: float = 1.0,
    detection_hyp_prior_alpha: float = 10.0,
    detection_i_prior_alpha: float = 100.0,
    detection_gi_prior_alpha: float = 200.0,
    gene_add_alpha_hyp_prior_alpha: float = 9.0,
    gene_add_alpha_hyp_prior_beta: float = 3.0,
    gene_add_mean_hyp_prior_alpha: float = 1.0,
    gene_add_mean_hyp_prior_beta: float = 100.0,
    stochastic_v_ag_hyp_prior_alpha: float = 12.0,
    stochastic_v_ag_hyp_prior_beta: float = 3.0,
    **kwargs,
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
    num_tfs = tf_indices.shape[0]
    batch_size = num_cells

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
    # sample a *single* global scaling factor
    T_min, T_max = T_limits
    T_scaling = numpyro.sample("T_scaling", dist.Beta(1.0, 3.0))
    # total_span = (T_max - T_min) * T_scaling

    # # build *static‐shape* grid (always N_steps long)
    # abs_grid   = T_min + times_norm * (T_max - T_min)
    # times_grid = T_scaling * abs_grid

    total_span = (T_max - T_min) * T_scaling

    # 2) build *static‐shape* grid (always N_steps long)
    times_grid = T_min + times_norm * total_span
    # dt = dt_norm * total_span

    # convert your absolute prior_time (if any) into a [0,1] loc/scale
    if prior_time is None:
        prior_time = T_min + (T_max - T_min) / 2
        prior_time_sd = prior_timespan / 2.0
    else:
        prior_time_sd = prior_timespan / 12.0

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

    # ============= Expression model =============== #

    # scale of alpha
    alpha_0 = numpyro.sample(
        "alpha_0",
        dist.Gamma(1.0, 1.0, validate_args=True).expand([num_genes]).to_event(1),
    )

    # Initial Conditions for ODE, sampling only for spliced and unspliced
    initial_state_2d = numpyro.sample(
        "initial_state_2d",
        dist.Gamma(1.0, 1.0, validate_args=True).expand([1, num_genes, 2]).to_event(1),
    )

    # Create the third dimension containing proteins, only for TFs:
    third_dimension = jnp.zeros((1, num_genes))
    third_dimension = third_dimension.at[0, tf_indices].set(
        numpyro.sample(
            "initial_state_tf",
            dist.Gamma(1.0, 1.0, validate_args=True).expand([len(tf_indices)]),
        )
    )

    # Concatenate the dimensions to form the final initial state
    initial_state = jnp.concatenate(
        [initial_state_2d, third_dimension[..., None]], axis=-1
    )

    n_keys = 2
    base_key = numpyro.prng_key()
    all_keys = jax.random.split(base_key, n_keys)
    std1 = jnp.sqrt(2.0 / (num_tfs + hidden_units))
    std2 = jnp.sqrt(2.0 / (hidden_units + num_genes))

    H = hidden_units
    W1 = numpyro.param(
        "W1", jax.random.normal(all_keys[0], (tf_indices.shape[0], H)) * std1
    )
    b1 = numpyro.param("b1", jnp.zeros((H,)))
    W2 = numpyro.param(
        "W2", jax.random.normal(all_keys[1], (H, data.shape[1])) * std2
    )
    b2 = numpyro.param("b2", jnp.zeros((data.shape[1],)))
    hill_params = {"W1": W1, "b1": b1, "W2": W2, "b2": b2}

    # Prepare Parameters for ODE Solver
    ode_args = (alpha_0, beta_g, gamma_g, lamda, kappa, hill_params, tf_indices)

    # Run euler integration
    key = numpyro.prng_key()
    sol_grid = euler_integrator(times_grid, initial_state, dstate_dt, ode_args, key)

    # Interpolate each cell’s trajectory at its sampled time T_c
    sol_at_cells = interpolate_solution(sol_grid, times_grid, T_c)

    # Track as predictions_rearranged for compatibility purposes with some plotting functions
    numpyro.deterministic('predictions_rearranged', sol_at_cells)

    # Extract unspliced & spliced for your likelihood
    mu_expression = jnp.clip(sol_at_cells[:,0,:, :2], 0, 1e5)

    # Wiggliness penalty (sum of squared curvature)
    d1 = sol_grid[1:] - sol_grid[:-1]
    d2 = d1[1:] - d1[:-1]
    penalty = jnp.sum(jnp.square(d2))/times_norm.shape[0]
    numpyro.factor("smoothness_penalty", - 10**6 * penalty)

    # ============= Detection efficiency of spliced and unspliced counts =============== #

    # Batch/Experiment-level scaling centered at 0.5
    with numpyro.plate("batch", n_batch):
        y_e = numpyro.sample(
            "detection_y_e",
            dist.Beta(detection_mean_hyp_prior_alpha,
                      detection_mean_hyp_prior_beta)
        )  # shape (n_batch,)

    # cell‐level scaling, centered at 1 (large variance)
    α_c = detection_hyp_prior_alpha
    with numpyro.plate("cells", batch_size):
        y_c = numpyro.sample(
            "detection_y_c",
            dist.Gamma(α_c, α_c)
        )  # shape (n_cells,)

    # Modality-level scaling, centered at 1 (moderate variance)
    detection_y_i = numpyro.sample(
        "detection_y_i",
        dist.Gamma(detection_i_prior_alpha, detection_i_prior_alpha, validate_args=True)
        .expand([1, 1, 2])
        .to_event(3),
    )

    # Modality and gene-level scaling, centered at 1 (small variance)
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
        y_e[batch_index][:, None, None]  # batch‐efficiency per cell
        * y_c[:, None, None]              # cell‐scale
        * detection_y_i                   # modality‐level
        * detection_y_gi                  # gene‐modality‐level
        * M_c                             # metacell size
    )

    mu = numpyro.deterministic("mu", (mu_expression + additive_term) * normalizing_term)

    # ===================== DATA likelihood ======================= #

    concentration = stochastic_v_ag * M_c
    rate = concentration / mu

    # Likelihood (sampling distribution)
    # We apply a scale factor so that the negative log-likelihood is multiplied
    # by (total_num_cells / batch_size). That ensures an unbiased gradient estimate.
    scale_factor = total_num_cells / batch_size
    with scale(scale=scale_factor):
        data_target = numpyro.sample(
            "data_target", dist.GammaPoisson(concentration, rate), obs=data
        )

# ---------- GRN Linearization Utilities  ----------

def _maybe_get_cell_indices(posterior):
    """
    Try to find which cells were used for predictions (if Predictive / minibatching was used).
    Mirrors the helper used in ATAC_RNA_v2.
    """
    for where in ("means", "samples", "params", None):
        container = posterior if where is None else posterior.get(where, {})
        if isinstance(container, dict) and "cell_indices" in container:
            idx = np.array(container["cell_indices"])
            if idx.ndim > 1:  # if per-draw, take the first draw (usually constant across draws)
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
        if name in posterior:
            return jnp.array(posterior[name])
    raise KeyError(f"Could not find '{name}' in posterior (checked means, params, samples, top-level).")


def _mlp_hidden(ptf, W1, b1):
    # ptf: (T,), W1: (T, H), b1: (H,) -> h: (H,)
    return jax.nn.elu(jnp.dot(ptf, W1) + b1)

def _mlp_logits(ptf, W1, b1, W2, b2):
    # -> logits over genes (G,)
    h = _mlp_hidden(ptf, W1, b1)
    return jnp.dot(h, W2) + b2

def _mlp_reg(ptf, W1, b1, W2, b2):
    # positive regulation via softplus
    return jax.nn.softplus(_mlp_logits(ptf, W1, b1, W2, b2))


def linearize_grn_at_p(
    p_ref: jnp.ndarray,
    *,
    tf_indices: jnp.ndarray,
    hill_params: dict,
    alpha_0: jnp.ndarray,
):
    """
    Linearize the 2-layer TF->gene MLP around a reference protein vector p_ref (G,).

    Returns a dict with:
      - 'J_tf_to_hidden' : (T, H)
      - 'J_tf_to_logits' : (T, G)
      - 'J_tf_to_reg'    : (T, G)
      - 'J_tf_to_alpha'  : (T, G)   (alpha = alpha_0 * reg)
      - 'h_ref'          : (H,)
      - 'logits_ref'     : (G,)
      - 'reg_ref'        : (G,)
      - 'alpha_ref'      : (G,)
      - 'ptf_ref'        : (T,)
    """
    W1, b1, W2, b2 = hill_params["W1"], hill_params["b1"], hill_params["W2"], hill_params["b2"]

    # restrict to TF block
    ptf_ref = p_ref[tf_indices]  # (T,)

    # handy closures for jacobians
    f_h      = lambda ptf: _mlp_hidden(ptf, W1, b1)                 # (T,) -> (H,)
    f_logits = lambda ptf: _mlp_logits(ptf, W1, b1, W2, b2)         # (T,) -> (G,)
    f_reg    = lambda ptf: _mlp_reg(ptf, W1, b1, W2, b2)            # (T,) -> (G,)
    f_alpha  = lambda ptf: alpha_0 * f_reg(ptf)                     # (T,) -> (G,)

    # reference values
    h_ref      = f_h(ptf_ref)               # (H,)
    logits_ref = f_logits(ptf_ref)          # (G,)
    reg_ref    = f_reg(ptf_ref)             # (G,)
    alpha_ref  = alpha_0 * reg_ref          # (G,)

    # forward-mode Jacobians
    J_tf_to_hidden = jacfwd(f_h)(ptf_ref)           # (T, H)
    J_tf_to_logits = jacfwd(f_logits)(ptf_ref)      # (T, G)
    J_tf_to_reg    = jacfwd(f_reg)(ptf_ref)         # (T, G)
    J_tf_to_alpha  = jacfwd(f_alpha)(ptf_ref)       # (T, G)

    return {
        "J_tf_to_hidden": J_tf_to_hidden,
        "J_tf_to_logits": J_tf_to_logits,
        "J_tf_to_reg":    J_tf_to_reg,
        "J_tf_to_alpha":  J_tf_to_alpha,
        "h_ref":          h_ref,
        "logits_ref":     logits_ref,
        "reg_ref":        reg_ref,
        "alpha_ref":      alpha_ref,
        "ptf_ref":        ptf_ref,
    }


def linearize_grn_batched(
    p_refs: jnp.ndarray,   # (K, G)
    *,
    tf_indices: jnp.ndarray,
    hill_params: dict,
    alpha_0: jnp.ndarray,
):
    """
    Vectorized wrapper over K reference protein vectors.
    Returns a dict with each entry stacked on a leading K dimension.
    """
    outs = [linearize_grn_at_p(p_refs[i], tf_indices=tf_indices, hill_params=hill_params, alpha_0=alpha_0)
            for i in range(p_refs.shape[0])]
    keys = outs[0].keys()
    return {k: jnp.stack([o[k] for o in outs], axis=0) for k in keys}


def _extract_proteins_from_posterior(posterior):
    """
    Get proteins per cell from posterior['means']['predictions_rearranged'].
    Handles both shapes:
      (cells, genes, 3)          -> direct RNA_2layers_ManualEuler
      (cells, paths, genes, 3)   -> fallback (take path 0)
    Returns array (cells, genes).
    """
    sol = _get_posterior_array(posterior, "predictions_rearranged")
    if sol.ndim == 3:
        # (cells, G, 3)
        return jnp.array(sol[..., 2])
    elif sol.ndim == 4:
        # (cells, P, G, 3)  -- keep behavior consistent with ATAC_RNA_v2: take path 0
        return jnp.array(sol[:, 0, :, 2])
    else:
        raise ValueError(
            f"'predictions_rearranged' has unexpected ndim={sol.ndim}. "
            "Expected 3 (cells, genes, 3) or 4 (cells, paths, genes, 3)."
        )


def linearize_per_celltype(
    adata_rna,
    posterior,
    model_input,
    *,
    cell_type_key: str = "RNA_cell_type",
):
    """
    Build per-cell-type reference protein vectors and run batched linearization
    for RNA_2layers_ManualEuler.

    Returns
    -------
    lin_batch : dict of arrays
        Output of `linearize_grn_batched` with leading dim = #cell types.
        Includes Jacobians:
          - J_tf_to_hidden : (K, T, H)
          - J_tf_to_logits : (K, T, G)
          - J_tf_to_reg    : (K, T, G)
          - J_tf_to_alpha  : (K, T, G)
        And reference values at each cell-type mean point.
    labels : np.ndarray
        Cell-type names aligned with lin_batch's leading dimension.
    """
    # 1) proteins per cell from posterior predictions
    mu_protein = _extract_proteins_from_posterior(posterior)  # (cells_pred, G)

    # 2) align cell-type vector to the cells used in predictions
    ct_full = adata_rna.obs[cell_type_key].astype(str).to_numpy()
    cell_idx = _maybe_get_cell_indices(posterior)
    if cell_idx is not None:
        ct_col = ct_full[cell_idx]
        if mu_protein.shape[0] != ct_col.shape[0]:
            raise ValueError(
                f"predictions_rearranged has {mu_protein.shape[0]} cells but "
                f"cell_indices gives {ct_col.shape[0]}"
            )
    else:
        if mu_protein.shape[0] != ct_full.shape[0]:
            raise ValueError(
                f"predictions_rearranged has {mu_protein.shape[0]} cells but "
                f"adata_rna has {ct_full.shape[0]}. Provide cell_indices in posterior."
            )
        ct_col = ct_full

    # 3) compute mean protein abundance per cell type
    unique_ct = np.unique(ct_col)
    p_refs = []
    labels = []
    for ct in unique_ct:
        mask = (ct_col == ct)
        if np.any(mask):
            p_refs.append(mu_protein[np.where(mask)[0]].mean(axis=0))  # (G,)
            labels.append(ct)

    if not p_refs:
        raise ValueError(f"No cells found for any cell type in '{cell_type_key}'.")

    p_refs = jnp.stack([jnp.array(x) for x in p_refs], axis=0)  # (K, G)
    labels = np.array(labels)

    # 4) collect parameters (robust to storage location)
    W1 = _get_posterior_array(posterior, "W1")
    b1 = _get_posterior_array(posterior, "b1")
    W2 = _get_posterior_array(posterior, "W2")
    b2 = _get_posterior_array(posterior, "b2")
    alpha_0 = _get_posterior_array(posterior, "alpha_0")

    hill_params = {"W1": W1, "b1": b1, "W2": W2, "b2": b2}

    # 5) run batched linearization
    lin_batch = linearize_grn_batched(
        p_refs,
        tf_indices=model_input["tf_indices"],
        hill_params=hill_params,
        alpha_0=alpha_0,
    )

    return lin_batch, labels

