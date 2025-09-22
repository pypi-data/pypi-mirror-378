from typing import Any, Dict, List, Optional

import jax
import jax.numpy as jnp
import numpy as np
from numpyro.infer import Predictive


def extract_posterior_means(
    model: Any,
    guide: Any,
    svi: Any,
    svi_state: Any,
    model_input: Dict[str, Any],
    deterministic_sites: List[str],
    num_det_samples: int = 2,
    sample_n_cells: Optional[int] = 100,
    rng_seed: int = 0,
    param_names = None,
) -> Dict[str, Any]:

    """
    Extracts posterior mean estimates for all latent variables and selected model parameters,
    with optional subsampling for large cell-specific deterministic outputs.

    This function is designed for memory-efficient posterior extraction after training
    with NumPyro SVI. It collects:

      1. **Latent variable means** (both global and local) from the variational guide
         for all cells.
      2. **Deterministic site means** (e.g., derived quantities computed inside the model)
         by running the model with the learned variational parameters and averaging over
         a small number of deterministic forward passes.
      3. **Learned model parameters** declared via `numpyro.param` (e.g., `W1`, `b1`, `W2`, `b2`)
         added directly to `"means"` so they can be used in downstream analysis like
         linearization, without needing special handling.

    For deterministic sites with a cell-specific dimension, a representative subset of cells
    can be selected to reduce memory usage. This subset is chosen by sorting cells along
    their posterior mean of `t_c` (inferred time) and taking evenly spaced indices to
    cover the full trajectory.

    Parameters
    ----------
    model : Callable
        The NumPyro model function.
    guide : Callable
        The variational guide used for SVI.
    svi : numpyro.infer.SVI
        The fitted SVI object.
    svi_state : Any
        The trained SVI state containing learned parameters.
    model_input : dict
        Dictionary of inputs to the model (and guide). Must include "data",
        "obs2sample", "M_c", and any other required arguments. Optional key:
        `"data_atac"` if the model has ATAC modality.
    deterministic_sites : list of str
        Names of deterministic sites (from `numpyro.deterministic`) whose posterior means
        should be extracted. For large per-cell outputs, these will be computed only for
        a subsample of cells.
    num_det_samples : int, default=2
        Number of stochastic forward passes to average over when estimating
        deterministic site means.
    sample_n_cells : int or None, default=100
        If set to a positive integer, the number of representative cells to select for
        deterministic site evaluation. If `None`, all cells are used.
    rng_seed : int, default=0
        Random seed for deterministic site evaluation.
    param_names : list of str or None, optional
        Names of `numpyro.param` parameters to also include in `"means"`. If `None`, no
        additional params are added.

    Returns
    -------
    dict
        A dictionary with:
          - `"means"` : dict mapping parameter/site names → NumPy arrays of posterior means.
          - `"cell_indices"` : 1D NumPy array of selected cell indices, only if
            `sample_n_cells` was used.

    Notes
    -----
    - Latent variable means come directly from the variational distribution
      (via `guide.extract_all_means`).
    - Deterministic site means are estimated from forward passes with fixed
      variational parameters.
    - Parameters from `numpyro.param` are inserted into `"means"` to make them
      accessible in the same way as sampled variables.
    - This function does **not** store full posterior samples, only means.
    """

    # 1) get variational params & stop gradients
    params = svi.get_params(svi_state)
    params = jax.tree_util.tree_map(jax.lax.stop_gradient, params)
    data_atac = model_input.get("data_atac", None)

    # 2) FULL latent means on all cells
    #    extract_all_means returns (global_dict, local_dict)
    g_full, l_full = guide.extract_all_means(svi_state, svi, model_input["data"],  model_input['obs2sample'], model_input['M_c'], data_atac = data_atac)

    # 3) remove any deterministic_sites so we only handle them below
    for ds in deterministic_sites:
        g_full.pop(ds, None)
        l_full.pop(ds, None)

    # 4) assemble the full-means map
    means: Dict[str, np.ndarray] = {}
    means.update({k: np.array(v) for k, v in g_full.items()})
    means.update({k: np.array(v) for k, v in l_full.items()})
    # now means["t_c"] is the full vector for all cells

    # 5) if you need to subsample cells for deterministic sites, pick indices
    mi = dict(model_input)
    selected: Optional[np.ndarray] = None
    if sample_n_cells is not None:
        # get total number of cells
        t_c_full = np.array(l_full["t_c"])
        total_cells = t_c_full.shape[0]
        # clamp to [0, total_cells]
        k = min(sample_n_cells, total_cells)

        if k > 0:
            # sort cells by their posterior t_c‐mean
            order = np.argsort(t_c_full)
            # generate k positions evenly spaced from 0 to total_cells-1
            positions = np.linspace(0, total_cells - 1, num=k)
            positions = positions.astype(int)
            # pick the cell indices that span the full range
            sel = order[positions]
            selected = sel

            # slice the inputs for predictive
            for key in ("data", "batch_index", "M_c", "prior_time", "obs2sample"):
                mi[key] = mi[key][sel]

    # 6) run Predictive *only* for deterministic sites over the subsample
    if deterministic_sites:
        n_samp = max(1, num_det_samples)
        pred = Predictive(
            model,
            guide=guide,
            params=params,
            return_sites=deterministic_sites,
            num_samples=n_samp,
        )
        draws = pred(jax.random.PRNGKey(rng_seed), **mi)
        # average out the sample‐axis
        for site in deterministic_sites:
            means[site] = np.array(draws[site].mean(axis=0))

    # --- Add numpyro.param entries to 'means' as-if they were posterior means ---
    # Extend this tuple if you introduce more learned parameters you want exposed.

    if param_names is not None:
            for name in param_names:
               if name in params:  # SVI params returned by svi.get_params(svi_state)
                   means[name] = np.asarray(params[name])

    # 7) build output
    out: Dict[str, Any] = {"means": means}
    if selected is not None:
        out["cell_indices"] = selected
    return out

def extract_posterior_estimates(
    model,
    guide,
    svi,
    svi_state,
    model_input: dict = None,
    quantiles: list = [0.5, 0.05, 0.95],
    num_samples: int = 0,
    modes: list = [],
    deterministic_sites: list = [],
):
    """
    Extract posterior estimates.

    This function returns transformed quantiles/medians, posterior samples,
    and if mode 1 is specified, the posterior mean estimates (combining global
    and local parameters) using the guide's extract_all_means method. It also returns
    deterministic site samples if deterministic sites is specified.

    Parameters
    ----------
    model : Callable
        The model used in SVI.
    guide : Callable
        The autoguide used in SVI.
    svi : SVI
        The trained SVI object.
    svi_state : SVIState
        The SVI state containing learned parameters.
    model_input : dict, optional
        Dictionary containing the model inputs, as returned from the train_svi function.
    quantiles : list of float, optional
        A list of quantiles to extract (e.g. [0.5, 0.05, 0.95]).
    num_samples : int, optional
        Number of posterior samples to draw (0 means no sampling).
    modes : list, optional
        A list of mode codes. If 1 is in modes, the function extracts the mean
        (using guide.extract_all_means) and saves it under key 'means'.
    deterministic_sites : list, optional
        A list with names of deterministic sites to extract. If num_samples is 0
        it will use 5 samples by default.

    Returns
    -------
    results : dict
        A dictionary with keys:
          - "quantiles": Quantile estimates (if quantiles other than 0.5 are provided).
          - "median": Median estimates (if 0.5 is in quantiles).
          - "posterior_samples": Samples from the posterior (if num_samples > 0).
          - "means": Combined posterior means (global and local) if 1 is in modes.
    """
    # 1) Get the raw variational parameters.
    raw_params = svi.get_params(svi_state)
    # Stop gradients to force the values to be concrete.
    raw_params = jax.tree_util.tree_map(jax.lax.stop_gradient, raw_params)

    results = {}

    # 2) Extract transformed quantiles (excluding 0.5) and median if needed
    quantiles_to_extract = [q for q in quantiles if q != 0.5]
    if quantiles_to_extract:
        results["quantiles"] = guide.quantiles(raw_params, quantiles_to_extract)
    if 0.5 in quantiles:
        results["median"] = guide.median(raw_params)

    # 3) Draw posterior samples if requested
    if num_samples > 0:
        rng_key = jax.random.PRNGKey(0)
        posterior_samples = guide.sample_posterior(
            rng_key, raw_params, sample_shape=(num_samples,)
        )
        results["posterior_samples"] = posterior_samples

    # 4) If mode 1 is specified, extract the combined posterior means.
    if 1 in modes:
        if model_input is None or "data" not in model_input:
            raise ValueError(
                "To extract means, model_input must contain the key 'data'."
            )
        # Use the guide's extraction function to obtain global and local means.
        global_means, local_means = guide.extract_all_means(
            svi_state, svi, model_input["data"], model_input['obs2sample'], model_input['M_c'],
        )
        # Combine the dictionaries. In case of duplicate keys, local_means will override.
        combined_means = {**global_means, **local_means}
        results["means"] = combined_means

    # 5) Return deterministic sites if requested:

    if deterministic_sites:
        rng_key = jax.random.PRNGKey(0)
        if num_samples == 0:
            num_samples = 1
        predictive = Predictive(
            model,
            guide=guide,  # include the guide so that latent variables come from the variational posterior
            params=raw_params,
            return_sites=deterministic_sites,
            num_samples=num_samples,
        )
        posterior_samples = predictive(rng_key, **model_input)

        results["deterministic"] = posterior_samples

    return results
