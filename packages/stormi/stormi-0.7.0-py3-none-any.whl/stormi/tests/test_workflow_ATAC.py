import anndata as ad
import jax.numpy as jnp
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure

###############################################################################
# Monkey-patch Gamma distribution to skip validate_args in tests
from numpyro.distributions.continuous import Gamma

_orig_gamma_init = Gamma.__init__

def _no_validate_gamma_init(self, concentration, rate, validate_args=True):
    _orig_gamma_init(self, concentration, rate, validate_args=False)

Gamma.__init__ = _no_validate_gamma_init
###############################################################################

from numpyro.infer.initialization import init_to_mean

from stormi.guides.AmortizedNormal import AmortizedNormal, warm_up_guide
from stormi.models.ATAC_RNA_v2 import linearize_per_celltype, model
from stormi.plotting import plot_elbo_loss
from stormi.posterior import extract_posterior_means
from stormi.train import train_svi_jit

###############################################################################
# Fixtures
###############################################################################

@pytest.fixture(scope="module")
def adata_rna():
    """
    Minimal AnnData with an RNA_cell_type column so linearize_per_celltype can group.
    """
    n_cells = 3
    n_genes = 4
    X = np.ones((n_cells, n_genes))
    obs = pd.DataFrame(
        {"RNA_cell_type": ["typeA", "typeB", "typeA"]},
        index=[f"cell{i}" for i in range(n_cells)],
    )
    var = pd.DataFrame(index=[f"gene{i}" for i in range(n_genes)])
    return ad.AnnData(X=X, obs=obs, var=var)

@pytest.fixture(scope="module")
def fake_model_input():
    """
    Minimal fake model_input dict (skips prepare_model_input).
    Shapes are small but consistent with the model.
    """
    num_cells = 3
    num_genes = 4
    num_regions = 5
    num_tfs = 2

    return {
        "data": jnp.ones((num_cells, num_genes, 2)),          # RNA: [unspliced, spliced]
        "data_atac": jnp.ones((num_cells, num_regions)),      # ATAC counts
        "M_c": jnp.ones((num_cells, 1, 1)),                   # metacell size
        "batch_index": jnp.zeros(num_cells, dtype=int),
        "tf_indices": jnp.arange(num_tfs),
        "motif_mask": jnp.ones((num_tfs, num_regions)),
        "region_tf_pairs": jnp.array([[0, 0], [1, 1]]),       # (region, TF)
        "region_gene_pairs": jnp.array([[0, 0], [1, 1]]),     # (region, gene)
        "region_tf_gene_triplets": jnp.array([[0, 0, 0], [1, 1, 1]]),
        "region_tf_indices": jnp.array([0, 1]),
        "gene_indices": jnp.array([0, 1]),
        "num_regions": num_regions,
        "total_num_cells": num_cells,
        "n_batch": 1,
        "prior_time": jnp.linspace(0, 1, num_cells),
        "prior_timespan": 1.0,
        "known_mot_idx": jnp.array([0, 1]),
        "unknown_mot_idx": jnp.array([2, 3]),
        "T_limits": (0.0, 1.0),
        "obs2sample": jnp.ones((num_cells, 1)),
        "times_norm": jnp.linspace(0, 1, 10),
        "num_hidden": 2,
    }

@pytest.fixture(scope="module")
def guide(fake_model_input):
    """
    Build AmortizedNormal guide via warm-up.
    """
    warm_params = warm_up_guide(model, fake_model_input)
    return AmortizedNormal(
        model,
        init_net_params=warm_params,
        init_loc_fn=init_to_mean,
        predict_detection_l_c=True,
    )

@pytest.fixture(scope="module")
def svi_results(guide, fake_model_input):
    """
    Run a couple of SVI iterations and return:
    (guide, svi, svi_state, losses)
    """
    guide_out, svi, svi_state, losses = train_svi_jit(
        model,
        guide,
        fake_model_input,
        max_iterations=2,
        cell_batch_size=2,
        log_interval=1,
        min_lr=1e-3,
        max_lr=1e-2,
        ramp_up_fraction=0.5,
    )
    return guide_out, svi, svi_state, losses

@pytest.fixture(scope="module")
def posterior_means(svi_results, fake_model_input):
    """
    Compute posterior means once and reuse across tests.
    """
    guide_out, svi, svi_state, _ = svi_results
    posterior = extract_posterior_means(
        model,
        guide_out,
        svi,
        svi_state,
        model_input=fake_model_input,  # use the same model_input we trained with
        deterministic_sites=["mu", "d_cr", "predictions_rearranged", "mu_atac", "T_c"],
        num_det_samples=1,
        sample_n_cells=5000,
    )
    return posterior

###############################################################################
# Tests
###############################################################################

@pytest.mark.slow
def test_svi_losses(svi_results):
    """
    Ensure losses is a non-empty list.
    """
    _, _, _, losses = svi_results
    assert isinstance(losses, list)
    assert len(losses) > 0

def test_plot_elbo_loss(svi_results):
    """
    Test that plot_elbo_loss returns either None or a Figure.
    """
    _, _, _, losses = svi_results
    fig = plot_elbo_loss(losses)
    assert fig is None or isinstance(fig, Figure)

def test_posterior_extraction(posterior_means):
    """
    Smoke check the posterior keys exist.
    """
    posterior = posterior_means
    for key in ["mu", "d_cr", "predictions_rearranged", "mu_atac", "T_c"]:
        assert key in posterior["means"]

def test_linearize_per_celltype(posterior_means, adata_rna, fake_model_input):
    """
    Use the already-generated posterior to test linearize_per_celltype.
    Assert the returned dict has 7 keys.
    """
    posterior = posterior_means
    lin_batch, labels = linearize_per_celltype(
        adata_rna,
        posterior,
        fake_model_input,  # pass the same model_input
        cell_type_key="RNA_cell_type",
    )
    assert isinstance(lin_batch, dict)
    assert len(lin_batch.keys()) == 7
    assert labels.shape[0] > 0
