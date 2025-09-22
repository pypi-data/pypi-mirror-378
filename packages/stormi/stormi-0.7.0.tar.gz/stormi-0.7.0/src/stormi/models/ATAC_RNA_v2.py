from collections import OrderedDict
from functools import partial
from numbers import Real
from typing import Any, Callable, Dict, List, Optional

import jax
import jax.numpy as jnp
import jax.random as random
import matplotlib.pyplot as plt
import numpy as np
import numpyro
import numpyro.distributions as dist
import pandas as pd
import scanpy as sc
import scipy.sparse as sp
from anndata import AnnData
from beartype import beartype
from diffrax import Euler, ODETerm, RecursiveCheckpointAdjoint, SaveAt, diffeqsolve
from einops import rearrange
from jax import lax
from jaxtyping import Float, jaxtyped
from numpyro.handlers import scale
from numpyro.infer import SVI, Predictive, Trace_ELBO
from numpyro.infer.autoguide import AutoNormal
from numpyro.optim import Adam

from stormi.models.utils import solve_DE, sort_times_over_all_cells


@beartype
def prepare_model_input(
    adata_rna: AnnData,
    adata_atac: AnnData,
    tf_list: List[str],
    motif_scores: pd.DataFrame,
    n_cells_col: Optional[str] = "n_cells",
    grid_type: str = "linear",
    N_steps: int = 100,
    prior_time_col: Optional[str] = None,
    batch_annotation: Optional[str] = None,
    species: Optional[str] = "human",
    prior_timespan: Optional[Real] = 40,
) -> Dict[str, Any]:
    """
    Prepare input data for the model by converting layers, stacking counts, and
    computing region–TF/gene relationships.

    This function performs the following steps:

      1. **Dense Conversion & Stacking RNA Data:**
         - Converts the `'spliced'` and `'unspliced'` layers of `adata_rna` to dense
           format using `convert_to_dense`.
         - Stacks the two arrays along a new axis (last dimension) and converts the
           resulting array to a JAX array.

      2. **ATAC Data Conversion:**
         - Converts the ATAC data (`adata_atac.X`) to a JAX array.

      3. **Additional Metadata Extraction:**
         - **M_c:** If `n_cells_col` is provided (not `None`), extracts that column from
           `adata_rna.obs` and reshapes it into a (cells, 1, 1) JAX array. Otherwise,
           sets `M_c` to an array of ones.
         - **batch_index:** If `batch_annotation` is provided, maps each unique batch
           to an integer and assigns these to cells. Otherwise, assigns a value of 1
           to all cells.
         - Determines the indices (and count) of transcription factors (TFs) in
           `adata_rna.var_names` using `tf_list`.
         - Determines the number of regions from the ATAC data.

      4. **Region–TF and Region–Gene Relationships:**
         - Computes `region_tf_pairs` using the `motif_scores` DataFrame
           together with `adata_atac` and `adata_rna`.
         - Computes `region_gene_pairs` from the RNA and ATAC AnnData objects.
         - Constructs all unique (region, TF, gene) triplets.
         - Computes the region–TF indices corresponding to each triplet.
         - Extracts gene indices from the triplets.

    Parameters
    ----------
    adata_rna : AnnData
        AnnData object containing RNA expression data with at least two layers:
        `'spliced'` and `'unspliced'`. Also requires an observation column (if used)
        containing the number of cells per metacell and a `var_names` attribute.
    adata_atac : AnnData
        AnnData object containing ATAC data. Its main count matrix is used.
    tf_list : List[str]
        List of transcription factor names.
    motif_scores : pd.DataFrame
        DataFrame (previously called moods_scores) that contains at least the columns used in
        the helper function `extract_region_tf_pairs` (by default, columns named `"0"` for regions
        and `"mouse_gene_name"` for TFs).
    n_cells_col : Optional[str], default "n_cells"
        Name of the column in `adata_rna.obs` that contains the number of cells in each metacell.
        If set to `None`, `M_c` is set to an array of ones.
    prior_time_col: Optional[str]
        Name of the column in `adata_rna.obs` that contains the prior expectation about the time for
        each cell in hours. By default it is set to `None`, so no prior knowledge is used.
    batch_annotation : Optional[str], default None
        Name of the column in `adata_rna.obs` that contains batch names.
        If `None`, all cells are assigned a batch value of 1. Otherwise, each unique batch is
        mapped to an integer.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
          - `data`: JAX array of shape (cells, features, 2) with stacked unspliced and spliced RNA counts.
          - `data_atac`: JAX array of ATAC counts.
          - `M_c`: JAX array of shape (cells, 1, 1) holding the per-cell metacell size.
          - `batch_index`: JAX array of batch indices for each cell.
          - `tf_indices`: JAX array of indices of transcription factors.
          - `num_tfs`: Total number of transcription factors (int).
          - `num_regions`: Total number of regions from the ATAC data (int).
          - `region_tf_pairs`: JAX array of region–TF pairs.
          - `region_gene_pairs`: JAX array of region–gene pairs with a weight.
          - `region_tf_gene_triplets`: JAX array of triplets (region, TF, gene).
          - `map_region_tf_to_index`: JAX array mapping each [region, TF] pair to its index.
          - `region_tf_indices`: JAX array of indices corresponding to the triplets.
          - `gene_indices`: JAX array of gene indices from the triplets.

    Example
    -------
    >>> inputs = prepare_model_input_data(adata_rna, adata_atac, tf_list, motif_scores,
    ...                                    n_cells_col="n_cells", batch_annotation="batch")
    >>> print(inputs["data"].shape)
    """
    # lazily import preprocessing functions, which require the preprocessing extras
    # $ pip install stormi[preprocessing]
    try:
        from stormi.preprocessing import (
            build_region_gene_pairs,
            construct_region_tf_gene_triplets,
            convert_to_dense,
            extract_region_tf_pairs,
            rhg_to_rh_indexing,
        )
    except ImportError:
        raise ImportError(
            "Preprocessing module dependencies are required for prepare_model_input. "
            "Install them with 'pip install stormi[preprocessing]'or 'uv sync --extra preprocessing'"
        )

    # --- Step 1: Convert and stack RNA layers ---
    spliced_dense = convert_to_dense(adata_rna.layers["spliced"])
    unspliced_dense = convert_to_dense(adata_rna.layers["unspliced"])
    # Stack along a new last axis: shape becomes (cells, features, 2)
    data = np.stack([unspliced_dense, spliced_dense], axis=-1)
    data = jnp.array(data)
    del unspliced_dense, spliced_dense

    # --- Step 2: Convert ATAC data ---
    data_atac = jnp.array(convert_to_dense(adata_atac.X))

    # --- Step 3: Extract additional metadata ---
    # M_c: Use provided column or default to ones.
    if n_cells_col is not None:
        M_c = jnp.array(
            np.expand_dims(
                np.expand_dims(adata_rna.obs[n_cells_col].to_numpy(), -1), -1
            )
        )
    else:
        M_c = jnp.ones((adata_rna.n_obs, 1, 1))
    total_num_cells = adata_rna.n_obs
    num_genes = adata_rna.n_vars

    # 3) prior time
    if prior_time_col is not None:
        prior_time = jnp.array(
            adata_rna.obs[prior_time_col].to_numpy(), dtype=jnp.float32
        )
        prior_timespan = float(prior_time.max() - prior_time.min())
    else:
        prior_time = None

    # batch_index: Map batch annotation to integer labels if provided; otherwise, assign 1 to all.
    if batch_annotation is not None:
        # Create a mapping from batch names to integers
        batch_series = adata_rna.obs[batch_annotation]
        unique_batches = batch_series.unique()
        batch_map = {batch: i for i, batch in enumerate(unique_batches)}
        batch_index = jnp.array(batch_series.map(batch_map).to_numpy())
    else:
        batch_index = jnp.zeros(adata_rna.n_obs, dtype=int)

    n_batch = len(jnp.unique(batch_index))

    # Determine which genes in adata_rna.var_names are TFs.
    is_tf = adata_rna.var_names.isin(tf_list)
    tf_indices = jnp.array(np.where(is_tf)[0])
    num_tfs = int(tf_indices.shape[0])
    num_regions = int(data_atac.shape[1])
    num_hidden = int(jnp.sqrt(num_tfs))*2

    # --- Step 4: Compute region–TF and region–gene relationships ---
    region_tf_pairs = extract_region_tf_pairs(motif_scores, adata_atac, adata_rna)
    region_gene_pairs = build_region_gene_pairs(adata_atac, adata_rna, species=species)
    region_gene_pairs = jnp.array(region_gene_pairs, dtype=jnp.int32)
    region_tf_gene_triplets = construct_region_tf_gene_triplets(
        region_tf_pairs, region_gene_pairs
    )
    region_tf_indices = rhg_to_rh_indexing(region_tf_gene_triplets, region_tf_pairs)
    gene_indices = region_tf_gene_triplets[:, 2]

    # ─ build flat index of known and unknown motif-region pairs
    known_mot_idx = region_tf_pairs[:, 0] * num_tfs + region_tf_pairs[:, 1]
    unknown_mot_idx = jnp.setdiff1d(jnp.arange(num_regions * num_tfs), known_mot_idx)

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

    # ========== 5) BUILD TIMEGRID ==========
    if prior_time_col is None:
        T_min = -prior_timespan / 2.0
        T_max = +prior_timespan / 2.0
    else:
        T_min = prior_time.min() - prior_timespan / 6.0
        T_max = prior_time.max() + prior_timespan / 6.0

    if grid_type == "linear":
        times_norm = jnp.linspace(0.0, 1.0, N_steps + 1)
    else:
        raise ValueError(f"Unknown grid_type '{grid_type}'.")

    # 6) dense mask shaped (num_tfs, num_regions)

    gene_to_tf = -jnp.ones((num_genes,), dtype=jnp.int32)
    gene_to_tf = gene_to_tf.at[tf_indices].set(jnp.arange(tf_indices.shape[0], dtype=jnp.int32))

    region_idxs = region_tf_pairs[:, 0].astype(jnp.int32)  # regions
    gene_idxs   = region_tf_pairs[:, 1].astype(jnp.int32)  # genes
    tf_rows     = gene_to_tf[gene_idxs]                    # tf‐row positions

    motif_mask = jnp.zeros((tf_indices.shape[0], num_regions), dtype=jnp.float32)
    motif_mask = motif_mask.at[tf_rows, region_idxs].set(1.0)

    return OrderedDict(
        [
            ("data", data),
            ("data_atac", data_atac),
            ("M_c", M_c),
            ("batch_index", batch_index),
            ("tf_indices", tf_indices),
            ("motif_mask", motif_mask),
            ("region_tf_pairs", region_tf_pairs),
            ("region_gene_pairs", region_gene_pairs),
            ("region_tf_gene_triplets", region_tf_gene_triplets),
            ("region_tf_indices", region_tf_indices),
            ("gene_indices", gene_indices),
            ("num_regions", num_regions),
            ("total_num_cells", total_num_cells),
            ("n_batch", n_batch),
            ("prior_time", prior_time),
            ("prior_timespan", prior_timespan),
            ("known_mot_idx", known_mot_idx),
            ("unknown_mot_idx", unknown_mot_idx),
            ("T_limits", (T_min, T_max)),
            ("obs2sample", obs2sample),
            ("times_norm", times_norm),
            ("num_hidden", num_hidden),
        ]
    )

@beartype
def sample_prior(
    model: Callable[..., Any],
    model_input: Dict[str, Any],
    num_samples: int = 5,
    seed: int = 42,
    *,
    sites: Optional[List[str]] = None,
    sample_n_cells: int = 0,
) -> Dict[str, Any]:
    """
    Runs prior predictive sampling for a given model, optionally on a subset
    of cells and only returning specified sites. Also returns which cells
    were selected (cell_indices).

    Parameters
    ----------
    model : Callable[..., Any]
        The NumPyro model to sample from.
    model_input : Dict[str, Any]
        Input dict for the model (must include at least "data", "num_regions",
        and region‐batching keys if used).
    num_samples : int
        Number of prior draws to generate.
    seed : int
        RNG seed for reproducibility.
    sites : list of str, optional
        If provided, only these sample sites will be returned.
    sample_n_cells : int
        If >0, uniformly subsample this many cells before running Predictive.

    Returns
    -------
    Dict[str, Any]
        A dict with:
          - each requested site → array of shape (num_samples, …)
          - "cell_indices" → 1D int array of length `sample_n_cells` (or all cells)
    """
    # 0) shallow‐copy inputs
    mi = dict(model_input)

    # 1) choose & record which cells to include
    n_cells = mi["data"].shape[0]
    if sample_n_cells and sample_n_cells < n_cells:
        idxs = jnp.arange(n_cells)
        selected = np.random.choice(idxs, sample_n_cells)
    else:
        selected = jnp.arange(n_cells)

    # slice all cell‐indexed arrays
    mi["data"] = mi["data"][selected, ...]
    mi["M_c"] = mi["M_c"][selected, ...]
    mi["batch_index"] = mi["batch_index"][selected]
    mi["prior_time"] = mi["prior_time"][selected]
    mi["obs2sample"] = mi["obs2sample"][selected,...]

    # 2) region‐level setup (unchanged)
    num_regions = model_input["num_regions"]
    all_region_indices = np.arange(num_regions)
    rng_local = np.random.default_rng(seed)
    init_region_batch = rng_local.choice(
        all_region_indices, size=num_regions, replace=False
    )

    # 3) draw from the prior with Predictive
    rng_key = random.PRNGKey(seed)
    predictive = Predictive(model, num_samples=num_samples, return_sites=sites)
    prior_samples = predictive(rng_key, **mi)

    # 4) attach which cells we used
    prior_samples["cell_indices"] = selected

    return prior_samples

def dstate_dt(t, state, args):
    (
        alpha0_g, beta_g, gamma_g,
        lamda,    kappa,
        tf_indices,
        motif_mask,
        W_tf1, b_tf1,
        W_tf2, b_tf2,
        w_rg,
        region_gene_pairs,
        b_g,
        num_genes,
        τ,
        binarized_counts
    ) = args

    # 1) unpack & clamp state
    u = jnp.clip(state[..., 0], 0, 1e3)
    s = jnp.clip(state[..., 1], 0, 1e3)
    p = jnp.clip(state[..., 2], 0, 1e3)

    # 2) TF → accessibility via your MLP helper
    #    (binarized=False so we get a real-valued accessibility)
    P = compute_accessibility(
        p,            # (cells, G)
        tf_indices,   # (T,)
        motif_mask,
        W_tf1, b_tf1, # (D, T), (D,)
        W_tf2, b_tf2, # (R, D), (R,)
        binarized_counts,         # binarized flag
        τ
    )  # returns (cells, R)

    # 3) aggregate region→gene
    edge_vals = P[:, region_gene_pairs[:, 0]]         # (cells, P)
    weighted  = edge_vals * w_rg[None, :]             # (cells, P)
    wP_swap   = jnp.swapaxes(weighted, 0, 1)          # (P, cells)
    summed    = jax.ops.segment_sum(
                   wP_swap,
                   region_gene_pairs[:, 1],
                   num_segments=num_genes
               )                                   # (G, cells)
    reg_in    = jnp.swapaxes(summed, 0, 1)            # (cells, G)

    # 4) transcription ODE
    alpha = alpha0_g * jax.nn.softplus(b_g + reg_in)
    du_dt = alpha - beta_g * u
    ds_dt = beta_g * u   - gamma_g * s

    dp_dt = jnp.zeros_like(u).at[..., tf_indices].set(
        lamda * s[..., tf_indices]
      - kappa * p[..., tf_indices]
    )

    return jnp.stack([du_dt, ds_dt, dp_dt], axis=-1)

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

def euler_integrator(
    times: jnp.ndarray,      # (L+1,)
    y0: jnp.ndarray,         # state at t0, shape (G,3)
    drift_fn: Any,           # f(t, y, args) -> dy/dt
    drift_args: Any,
    rng_key: jax.random.PRNGKey,
    sigma_noise: float = 1e-10,   # ← small noise scale
) -> jnp.ndarray:
    """
    Euler–Maruyama integrator: y_{n+1} = y_n + f(t_n,y_n)*dt + sigma_noise*sqrt(dt)*eps_n
    """
    dt = jnp.diff(times)  # (L,)
    # # draw one Gaussian noise array per step
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

def compute_accessibility(
    p: jnp.ndarray,           # (cells, G)
    tf_indices: jnp.ndarray,  # (T,)
    motif_mask: jnp.ndarray,  # (T, R)  1 if TF t has motif in region r
    W_tf1: jnp.ndarray,       # (D, T)
    b_tf1: jnp.ndarray,       # (D,)
    W_tf2: jnp.ndarray,       # (R, D)
    b_tf2: jnp.ndarray,       # (R,)
    binarized: bool = True,
    τ: float = 0.0,
) -> jnp.ndarray:
    """
    Region-wise masked MLP:
      1) Gate TF inputs by motif presence per region BEFORE the first layer.
      2) Compute region-specific hidden activations h[c, r, d].
      3) For each region r, apply its own output weights W_tf2[r, :].

    Shapes:
      p: (C, G), tf_indices: (T,), motif_mask: (T, R),
      W_tf1: (D, T), b_tf1: (D,), W_tf2: (R, D), b_tf2: (R,)
      returns: (C, R)
    """
    # Select TF proteins
    p_tf = p[:, tf_indices]  # (C, T)

    # First layer with region-wise masking:
    # h_linear[c, r, d] = sum_t p[c,t] * motif_mask[t,r] * W_tf1[d,t] + b_tf1[d]
    # Einsum dims: 'ct,tr,dt->crd'
    h_linear = jnp.einsum('ct,tr,dt->crd', p_tf, motif_mask, W_tf1) + b_tf1[None, None, :]
    h = jax.nn.elu(h_linear)  # (C, R, D)

    # Region-specific output: logits[c, r] = <h[c, r, :], W_tf2[r, :]> + b_tf2[r]
    logits = jnp.einsum('crd,rd->cr', h, W_tf2) + b_tf2[None, :]

    if binarized:
        return jax.nn.sigmoid(τ * logits)
    else:
        return jax.nn.softplus(logits) + 1e-5

# Define the complete NumPyro model
@beartype
def model(
    data: Any,
    data_atac: Any,
    M_c: Any,
    batch_index: Any,
    tf_indices: Any,
    motif_mask: Any,
    region_tf_pairs: Any,
    region_gene_pairs: Any,
    region_tf_gene_triplets: Any,
    region_tf_indices: Any,
    gene_indices: Any,
    num_regions: Any,
    times_norm: Any,
    num_hidden: int,
    total_num_cells: int,
    n_batch: int,
    prior_time: Any,
    prior_timespan: Any,
    known_mot_idx: Any,
    unknown_mot_idx: Any,
    T_limits: Any,
    obs2sample: Any,
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
    stochastic_v_ag_hyp_prior_alpha_atac: float = 9.0,
    stochastic_v_ag_hyp_prior_beta_atac: float = 3.0,
    binarized_counts: bool = False,
    **kwargs,
):
    """
    NumPyro model for coupled transcription, splicing, protein, chromatin dynamics.

    Args:
        data: Observed data array of shape (num_cells, num_genes, num_modalities).
        ... (other model inputs)
        ... (other hyperparameters for priors)
        key: Random number generator key.

    Returns:
        None. Defines the probabilistic model for inference.
    """
    num_cells, num_genes, num_modalities = data.shape
    num_tfs = tf_indices.shape[0]
    num_pairs = len(region_tf_pairs)
    num_rg_pairs = len(region_gene_pairs)
    num_rtg_triplets = len(region_tf_gene_triplets)
    num_regions_total = num_regions
    num_regions_batch = data_atac.shape[1]
    batch_size = num_cells

    # Prior for TF to hidden units MLP:

    # hidden layer size
    D = num_hidden

    # 1) first layer: TFs → hidden
    std1 = jnp.sqrt(2.0 / (num_tfs + D))
    W_tf1 = numpyro.sample(
        "W_tf1",
        dist.Normal(0.0, std1)
            .expand([D, num_tfs])
            .to_event(2),
    )  # (D, T)
    b_tf1 = numpyro.sample(
        "b_tf1",
        dist.Normal(0.0, 0.1)
            .expand([D])
            .to_event(1),
    )  # (D,)

    # 2) second layer: hidden → regions
    std2 = jnp.sqrt(2.0 / D)
    W_tf2 = numpyro.sample(
        "W_tf2",
        dist.Normal(0.0, std2)
            .expand([num_regions, D])
            .to_event(2),
    )  # (R, D)
    b_tf2 = numpyro.sample(
        "b_tf2",
        dist.Normal(0.0, 0.1)
            .expand([num_regions])
            .to_event(1),
    )  # (R,)

    # Temperature of sigmoid controlling ATAC:
    if binarized_counts:
        τ = numpyro.sample("tau", dist.Gamma(1.0, 1.0))
    else:
        τ = 1.0

    # Basal transcription rate
    alpha0_g = numpyro.sample(
        "alpha0_g",
        dist.Gamma(1.0, 1.0, validate_args=True).expand([num_genes]).to_event(1),
    )

    # Bias term for transcription rate function:
    b_g = numpyro.sample("b_g", dist.Normal(-1.0, 1.0).expand([num_genes]).to_event(1))

    w_rg = numpyro.sample(
        "w_rg",
        dist.Normal(0.0, 1.0).expand([num_rg_pairs]).to_event(1),
    )

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
    T_min, T_max = T_limits
    T_scaling = numpyro.sample("T_scaling", dist.Beta(1.0, 3.0))
    total_span = (T_max - T_min) * T_scaling

    # build *static‐shape* grid (always N_steps long)
    times_grid = T_min + times_norm * total_span

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

    # Concatenate the dimensions to form the final initial state:
    initial_state = jnp.concatenate(
        [initial_state_2d, third_dimension[..., None]], axis=-1
    )

    # Prepare Parameters for ODE Solver
    ode_args = (
        alpha0_g, beta_g, gamma_g,
        lamda, kappa,
        tf_indices,
        motif_mask,
        W_tf1, b_tf1,
        W_tf2, b_tf2,
        w_rg,
        region_gene_pairs,
        b_g,
        num_genes,
        τ,
        binarized_counts
    )

    # Then call your integrator with exactly that tuple:
    key = numpyro.prng_key()
    sol_grid = euler_integrator(times_grid, initial_state, dstate_dt, ode_args, key)

    # Interpolate each cell’s trajectory at its sampled time T_c
    sol_at_cells = interpolate_solution(sol_grid, times_grid, T_c)

    # Track as predictions_rearranged for compatibility purposes with some plotting functions
    numpyro.deterministic('predictions_rearranged', sol_at_cells)

    # Extract unspliced & spliced for your likelihood
    mu_expression = jnp.clip(sol_at_cells[:,0,:, :2], 0, 1e5)

    mu_protein = mu_expression[..., 2]

    # ============= ATAC model ======================

    d_cr = numpyro.deterministic(
        "d_cr",
        compute_accessibility(
            mu_protein,        # (cells, num_genes)
            tf_indices,        # (num_tfs,)
            motif_mask,
            W_tf1, b_tf1,      # (D, T), (D,)
            W_tf2, b_tf2,      # (R, D), (R,)
            binarized_counts,   # bool flag
            τ
        ),
    )

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

    # ============= Detection efficiency of ATAC counts =============== #

    # Batch/Experiment-level scaling centered at 0.5
    with numpyro.plate("batch", n_batch):
        l_e = numpyro.sample(
            "detection_mean_l_e",
            dist.Beta(1.0,
                      9.0)
        )  # shape (n_batch,)

    # cell‐level scaling, centered at 1 (large variance)
    α_c = detection_hyp_prior_alpha
    with numpyro.plate("cells", batch_size):
        l_c = numpyro.sample(
            "detection_l_c",
            dist.Gamma(α_c, α_c)
        )  # shape (n_cells,)

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

    # ========= Overdispersion for ATAC ============== #

    if not binarized_counts:

        stochastic_v_ag_hyp_atac = numpyro.sample(
            "stochastic_v_ag_hyp_atac",
            dist.Gamma(
                stochastic_v_ag_hyp_prior_alpha_atac, stochastic_v_ag_hyp_prior_beta_atac
            ),
        )

        stochastic_v_ag_inv_atac = numpyro.sample(
            "stochastic_v_ag_inv_atac",
            dist.Exponential(stochastic_v_ag_hyp_atac).expand([1, num_regions]).to_event(2),
        )

        stochastic_v_ag_atac = jnp.ones((1, 1)) / stochastic_v_ag_inv_atac**2

    # ===================== Expected value for RNA and ATAC counts======================= #

    additive_term = numpyro.deterministic(
        "additive_term", jnp.einsum("cb,bgi->cgi", obs2sample, s_g_gene_add)
    )

    normalizing_term = numpyro.deterministic(
        "normalizing_term",
        y_e[batch_index][:, None, None]  # batch‐efficiency per cell
        * y_c[:, None, None]              # cell‐scale
        * detection_y_i                   # modality‐level
        * detection_y_gi                  # gene‐modality‐level
        * M_c                             # metacell sized
    )

    mu = numpyro.deterministic("mu", (mu_expression + additive_term) * normalizing_term)

    if not binarized_counts:

        normalizing_term_atac = numpyro.deterministic(
            "normalizing_term_atac",
            l_e[batch_index][:,None]  # batch‐efficiency per cell
            * l_c[...,0]
            * M_c[...,0]                            # metacell size
        )

        mu_atac = numpyro.deterministic(
            "mu_atac", normalizing_term_atac * d_cr
        )

        concentration_atac = stochastic_v_ag_atac * M_c[..., 0]
        rate_atac = concentration_atac / mu_atac

    # ===================== DATA likelihood ======================= #

    concentration = stochastic_v_ag * M_c
    rate = concentration / mu

    # We apply a scale factor so that the negative log-likelihood is multiplied
    # by the ratio of the full dataset to the minibatch dataset, to have an unbiased gradient estimate.
    scale_factor_rna = total_num_cells / batch_size
    with scale(scale=scale_factor_rna):
        data_target = numpyro.sample(
            "data_target", dist.GammaPoisson(concentration, rate), obs=data
        )

    # # We further adjust the scale factor here to give equal weight to RNA and ATAC data
    # # no matter the number of features in each
    scale_factor_atac = scale_factor_rna# * 2 * num_genes / num_regions_batch

    if binarized_counts:
        # 1) flatten M_c → shape (num_cells,)
        M_c_cell = jnp.squeeze(M_c, axis=(1, 2))        # (cells,)

        # 2) make it a column vector → shape (cells, 1)
        M_c_trials = M_c_cell[:, None]                  # (cells, 1)

        # 3) compute intrinsic p ∈ [0,1]
        p_intrinsic = d_cr                              # (cells, regions)
        p_atac = (
            l_e[batch_index][:, None]  # → (cells, 1)
            * l_c[..., 0, None]        # → (cells, 1)
            * p_intrinsic              # → (cells, regions)
        )
        p_atac = numpyro.deterministic(
            "mu_atac", jnp.clip(p_atac, 1e-6, 1-1e-6))

        # 4) overdispersion φ
        φ = numpyro.sample("phi_atac", dist.Gamma(5.0, 1.0))
        α = φ * p_atac              # (cells, regions)
        β = φ * (1 - p_atac)        # (cells, regions)

        # 5) plate over cells, treating regions as an event
        with scale(scale=scale_factor_atac):
            with numpyro.plate("cells_atac", M_c_cell.shape[0]):
                numpyro.sample(
                    "data_target_atac",
                    dist.BetaBinomial(
                        total_count=M_c_trials,    # now (cells,1)
                        concentration1=α,         # (cells, regions)
                        concentration0=β          # (cells, regions)
                    ).to_event(1),                 # collapse the region dim into a single event
                    obs=data_atac                  # (cells, regions)
                )
    else:

        # --- original GammaPoisson on raw sums ---
        with scale(scale=scale_factor_atac):
            numpyro.sample(
                "data_target_atac",
                dist.GammaPoisson(concentration_atac, rate_atac),
                obs=data_atac,
            )

# --------- Downstream Analysis ------------

def _region_to_gene(
    P: jnp.ndarray,                 # (R,)
    w_rg: jnp.ndarray,              # (P,)
    region_gene_pairs: jnp.ndarray, # (P, 2) [region, gene]
    num_genes: int
) -> jnp.ndarray:
    """Aggregate region accessibility to a gene-level input (G,) using your w_rg + pairs."""
    edge_vals = P[region_gene_pairs[:, 0]]  # (P,)
    weighted  = edge_vals * w_rg            # (P,)
    reg_in_T  = jax.ops.segment_sum(weighted, region_gene_pairs[:, 1], num_segments=num_genes)
    return reg_in_T                          # (G,)


def _alpha_from_regin(alpha0_g: jnp.ndarray, b_g: jnp.ndarray, reg_in: jnp.ndarray):
    """α_g = α0_g * softplus(b_g + reg_in). Returns (alpha, z) with z=b_g+reg_in."""
    z = b_g + reg_in
    return alpha0_g * jax.nn.softplus(z), z

def _accessibility_single(
    p_full: jnp.ndarray,         # (G,)
    *,
    tf_indices: jnp.ndarray,     # (T,)
    motif_mask: jnp.ndarray,     # (T, R)
    W_tf1: jnp.ndarray, b_tf1: jnp.ndarray,   # (D,T), (D,)
    W_tf2: jnp.ndarray, b_tf2: jnp.ndarray,   # (R,D), (R,)
    binarized_counts: bool,
    tau: float
) -> jnp.ndarray:
    """
    Single-sample wrapper that reuses your batch `compute_accessibility`.
    Returns P (R,) for a single protein abundance vector `p_full`.
    """
    P = compute_accessibility(
        p_full[None, :], tf_indices, motif_mask,  # add cell axis
        W_tf1, b_tf1, W_tf2, b_tf2,
        binarized_counts, tau
    )  # -> (1, R)
    return P[0]

import jax
import jax.numpy as jnp
from jax import jacfwd


def linearize_grn_at_p(
    p_ref: jnp.ndarray,
    *,
    tf_indices: jnp.ndarray,
    motif_mask: jnp.ndarray,
    W_tf1: jnp.ndarray, b_tf1: jnp.ndarray,
    W_tf2: jnp.ndarray, b_tf2: jnp.ndarray,
    w_rg: jnp.ndarray,
    region_gene_pairs: jnp.ndarray,
    b_g: jnp.ndarray,
    alpha0_g: jnp.ndarray,
    num_genes: int,
    binarized_counts: bool,
    tau: float,
):
    def _set_tf_block(ptf): return p_ref.at[tf_indices].set(ptf)

    def _accessibility_single(p_full):
        P = compute_accessibility(
            p_full[None, :], tf_indices, motif_mask,
            W_tf1, b_tf1, W_tf2, b_tf2,
            binarized_counts, tau
        )
        return P[0]  # (R,)

    def f_region(ptf):       # (T,) -> (R,)
        return _accessibility_single(_set_tf_block(ptf))

    def f_gene_input(ptf):   # (T,) -> (G,)
        P = f_region(ptf)
        # (P,) weights over (pairs) to (G,)
        edge_vals = P[region_gene_pairs[:, 0]]
        weighted  = edge_vals * w_rg
        return jax.ops.segment_sum(weighted, region_gene_pairs[:, 1], num_segments=num_genes)

    def f_alpha(ptf):        # (T,) -> (G,)
        reg_in = f_gene_input(ptf)
        z = b_g + reg_in
        return alpha0_g * jax.nn.softplus(z)

    ptf_ref = p_ref[tf_indices]
    P_ref      = f_region(ptf_ref)
    reg_in_ref = f_gene_input(ptf_ref)
    z_ref      = b_g + reg_in_ref
    alpha_ref  = alpha0_g * jax.nn.softplus(z_ref)

    # Forward-mode Jacobians: shape (T, R) or (T, G)
    J_tf_to_region     = jacfwd(f_region)(ptf_ref)
    J_tf_to_gene_input = jacfwd(f_gene_input)(ptf_ref)
    J_tf_to_alpha      = jacfwd(f_alpha)(ptf_ref)

    return {
        "J_tf_to_region": J_tf_to_region,
        "J_tf_to_gene_input": J_tf_to_gene_input,
        "J_tf_to_alpha": J_tf_to_alpha,
        "P_ref": P_ref,
        "reg_in_ref": reg_in_ref,
        "alpha_ref": alpha_ref,
        "z_ref": z_ref,
    }

def linearize_grn_batched(
    p_refs: jnp.ndarray,   # (K, G)
    **kwargs
):
    """
    vmap over K reference protein vectors. Returns each entry stacked over K.
    """
    def _one(p_ref):
        return linearize_grn_at_p(p_ref, **kwargs)

    # vmap over dicts: collect keys manually
    K = p_refs.shape[0]
    outs = [_one(p_refs[i]) for i in range(K)]
    keys = outs[0].keys()
    return {k: jnp.stack([o[k] for o in outs], axis=0) for k in keys}

def _maybe_get_cell_indices(posterior):
    """Try to find the cell indices used for predictions, if any."""
    for where in ("means", "samples", None):
        container = posterior if where is None else posterior.get(where, {})
        if isinstance(container, dict) and "cell_indices" in container:
            idx = np.array(container["cell_indices"])
            # If per-draw, take the first draw (usually constant across draws)
            if idx.ndim > 1:
                idx = idx[0]
            return idx.astype(int)
    return None

def linearize_per_celltype(
    adata_rna,
    posterior,
    model_input,
    *,
    cell_type_key: str = "RNA_cell_type",
    binarized_counts: bool = False,
    tau: float = 1.0,
):

    """
    Build per-cell-type reference protein vectors and run batched linearization.

    Returns
    -------
    lin_batch : dict of arrays
        Output of `linearize_grn_batched` with leading dim = #cell types.
    labels : np.ndarray
        Cell-type names, aligned with lin_batch's leading dimension.
    """

    # 1) proteins from posterior predictions: (cells_pred, G)
    sol = posterior["means"]["predictions_rearranged"]
    mu_protein = sol[:, 0, :, 2]

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

    # 5) run batched linearization with posterior means
    lin_batch = linearize_grn_batched(
        p_refs,
        tf_indices=model_input["tf_indices"],
        motif_mask=model_input["motif_mask"],
        W_tf1=posterior["means"]["W_tf1"],
        b_tf1=posterior["means"]["b_tf1"],
        W_tf2=posterior["means"]["W_tf2"],
        b_tf2=posterior["means"]["b_tf2"],
        w_rg=posterior["means"]["w_rg"],
        region_gene_pairs=model_input["region_gene_pairs"],
        b_g=posterior["means"]["b_g"],
        alpha0_g=posterior["means"]["alpha0_g"],
        num_genes=adata_rna.n_vars,
        binarized_counts=binarized_counts,
        tau=float(tau),
    )

    return lin_batch, labels



