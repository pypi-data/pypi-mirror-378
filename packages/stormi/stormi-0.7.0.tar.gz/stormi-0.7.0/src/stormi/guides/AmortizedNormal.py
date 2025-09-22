from functools import partial
from typing import Optional

import jax
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
import optax
from numpyro.handlers import block, seed
from numpyro.infer import SVI, Trace_ELBO
from numpyro.infer.autoguide import AutoDelta, AutoGuideList, AutoNormal

# =============================================================================
# 1) Pure‐JAX amortization network forward pass
# =============================================================================

def _make_network_forward(
    pytree_params: dict,
    data_array: jnp.ndarray,
    obs2sample: jnp.ndarray,
    M_c: jnp.ndarray,
    predict_detection_y: bool,
    predict_detection_l: bool,
    predict_path_weights: bool,
    data_atac = None,
    include_batch: bool = False,
    use_hidden_layer: bool = False,
) -> tuple[jnp.ndarray, ...]:
    """
    Pure-JAX amortization network forward pass, with optional extra hidden layers.
    Returns outputs: (loc_t, scale_t, loc_y?, scale_y?, loc_l?, scale_l?, loc_z?, scale_z?)
    """
    n_cells, n_genes, n_mods = data_array.shape
    d_in = n_genes * n_mods

    # 1) flatten counts and adjust by metacell size
    data_2d = data_array.reshape((n_cells, d_in))
    per_cell = data_2d / (M_c.reshape((n_cells, 1)) + 1e-8)

    # 2) compute per-cell library size
    lib_raw = jnp.sum(per_cell, axis=1, keepdims=True)
    lib_feat = jnp.log1p(lib_raw / jnp.mean(lib_raw))

    if data_atac is not None:
        flat_atac = data_atac.reshape((n_cells, -1))
        lib_raw_atac = jnp.sum(flat_atac, axis=1, keepdims=True)
        lib_feat_atac = jnp.log1p(lib_raw_atac / jnp.mean(lib_raw_atac))

    # 3) normalize for biology trunk
    data_norm = per_cell / (lib_raw + 1e-8)
    feat = jnp.log1p(data_norm)

    # 4) shared hidden trunk
    h_shared = jax.nn.elu(feat @ pytree_params["V_shared"] + pytree_params["c_shared"])

    # 5) library embedding
    lib_emb = jax.nn.elu(lib_feat @ pytree_params["W_lib"] + pytree_params["b_lib"])

    if data_atac is not None:
        lib_emb_atac = jax.nn.elu(lib_feat_atac @ pytree_params["W_lib_atac"] + pytree_params["b_lib_atac"])

    # 6) batch embedding
    if include_batch:
        batch_emb = jax.nn.elu(obs2sample @ pytree_params["W_batch"] + pytree_params["b_batch"])
    else:
        batch_emb = jnp.zeros((n_cells, 0), dtype=h_shared.dtype)

    # 7) augmented features
    h_aug = jnp.concatenate([h_shared, lib_emb, batch_emb], axis=1)

    if data_atac is not None:
        h_aug_atac = jnp.concatenate([h_shared, lib_emb_atac, batch_emb], axis=1)

    outputs = []

    # ---- time head ----
    if use_hidden_layer:
        # first hidden layer
        h_t1 = jax.nn.elu(h_aug @ pytree_params["V_t_c"] + pytree_params["c_t_c"])
        # second hidden layer
        h_t2 = jax.nn.elu(h_t1 @ pytree_params["t_c_hidden_W"] + pytree_params["t_c_hidden_b"])
        t_out = h_t2 @ pytree_params["V_out_t_c"] + pytree_params["c_out_t_c"]
    else:
        h_t = jax.nn.elu(h_aug @ pytree_params["V_t_c"] + pytree_params["c_t_c"])
        t_out = h_t @ pytree_params["V_out_t_c"] + pytree_params["c_out_t_c"]
    loc_t = t_out[:, 0]
    scale_t = jax.nn.softplus(t_out[:, 1]) + 1e-3
    outputs += [loc_t, scale_t]

    # ---- detection_y head ----
    if predict_detection_y:
        if use_hidden_layer:
            h_y1 = jax.nn.elu(h_aug @ pytree_params["V_det"] + pytree_params["c_det"])
            h_y2 = jax.nn.elu(h_y1 @ pytree_params["det_hidden_W"] + pytree_params["det_hidden_b"])
            y_out = h_y2 @ pytree_params["V_out_det"] + pytree_params["c_out_det"]
        else:
            h_y = jax.nn.elu(h_aug @ pytree_params["V_det"] + pytree_params["c_det"])
            y_out = h_y @ pytree_params["V_out_det"] + pytree_params["c_out_det"]
        loc_y = y_out[:, 0]
        scale_y = jax.nn.softplus(y_out[:, 1]) + 1e-3
        outputs += [loc_y, scale_y]

    # ---- detection_l head ----
    if predict_detection_l:
        if use_hidden_layer:
            h_l1 = jax.nn.elu(h_aug_atac @ pytree_params["V_det_l"]
                              + pytree_params["c_det_l"])
            h_l2 = jax.nn.elu(h_l1      @ pytree_params["det_l_hidden_W"]
                              + pytree_params["det_l_hidden_b"])
            l_out = h_l2     @ pytree_params["V_out_det_l"] + pytree_params["c_out_det_l"]
        else:
            h_l = jax.nn.elu(h_aug_atac @ pytree_params["V_det_l"]
                             + pytree_params["c_det_l"])
            l_out = h_l      @ pytree_params["V_out_det_l"] + pytree_params["c_out_det_l"]
        loc_l   = l_out[:, 0]
        scale_l = jax.nn.softplus(l_out[:, 1]) + 1e-3
        outputs += [loc_l, scale_l]

    # ---- path_weights head ----
    if predict_path_weights:
        h_pw = jax.nn.elu(h_aug @ pytree_params["V_pw"] + pytree_params["c_pw"])
        z_out = h_pw @ pytree_params["V_out_pw"] + pytree_params["c_out_pw"]
        num_paths = z_out.shape[1] // 2
        loc_z = z_out[:, :num_paths]
        raw_scale_z = z_out[:, num_paths:]
        scale_z = jax.nn.softplus(raw_scale_z) + 1e-3
        outputs += [loc_z, scale_z]

    return tuple(outputs)

# JIT‐compile the network forward
_network_forward = jax.jit(
    _make_network_forward,
    static_argnames=(
        "predict_detection_y",
        "predict_detection_l",
        "predict_path_weights",
        "include_batch",
        "use_hidden_layer",
    ),
)

# =============================================================================
# 2) Rewrite amortized_guide to call the JIT‐compiled network_forward
# =============================================================================

def amortized_guide(
    *args,
    predict_detection_l_c: bool = False,
    predict_detection_y_c: bool = True,
    predict_path_weights: bool = False,
    use_hidden_layer: bool = False,
    hidden_dim: int = 256,
    shared_dim: int = 32,
    init_net_params: dict = None,
    init_seed: int = 0,
    include_batch: bool = False,
    noise_scale: float = 0.0,
    **kwargs,
):
    """
    An optimized amortized guide that JIT‐compiles the network forward pass once,
    then reuses it on each sample call. Registers all NN parameters with
    numpyro.param, then calls _network_forward(params, data, obs2sample, M_c, ...) in one shot.

    Args:
      - predict_detection_y_c: enable detection_y_c head
      - predict_detection_l_c: enable detection_l_c head
      - predict_path_weights:  enable path_weights head
      - use_hidden_layer:      insert per-head hidden layer
      - hidden_dim:            hidden layer size if used
      - shared_dim:            size of shared trunk
    """
    # Retrieve inputs
    data = kwargs.get("data", args[0] if args else None)
    data_atac  = kwargs.get("data_atac", None)
    obs2sample = kwargs.get("obs2sample")
    T_limits = kwargs.get("T_limits")
    M_c = kwargs.get("M_c")
    if data is None or obs2sample is None or M_c is None:
        raise ValueError("amortized_guide requires data, obs2sample, and M_c")

    # Setup RNG keys
    head_count = 1 + int(predict_detection_y_c) + int(predict_detection_l_c) + int(predict_path_weights)
    # per-head keys: hidden mapping (2) + first-layer mapping (2) + output mapping (2) if not hidden, or hidden(2)+output(2) if hidden
    keys_per_head = (2 + 2 + 2) if not use_hidden_layer else (2 + 2)
    total_keys = 6 + head_count * keys_per_head + 3
    all_keys = jax.random.split(jax.random.PRNGKey(init_seed), total_keys)
    idx_key = 0

    noise_key = all_keys[idx_key]
    idx_key += 1

    if noise_scale > 0.0:
        eps = numpyro.sample(
            "_amort_noise",
            dist.Normal(0, noise_scale)
                .expand(data.shape)
                .to_event(data.ndim),
            infer={"is_auxiliary": True},
        )
        mult = jnp.clip(1.0 + eps, a_min=0.0)
        data_for_forward = data * mult
    else:
        data_for_forward = data

    # Dimensions
    n_cells, n_genes, n_mods = data.shape
    H_shared = shared_dim
    lib_dim = 8
    batch_dim = 8 if include_batch else 0
    H_aug = H_shared + lib_dim + batch_dim
    out_dim = 2

    # init helper
    def make(name, shape, rng):
        if init_net_params and name in init_net_params:
            return init_net_params[name].astype(jnp.float32)
        return jax.random.normal(rng, shape, dtype=jnp.float32) * 0.01

    params = {}
    # shared trunk
    params['V_shared'] = numpyro.param('V_shared', make('V_shared', (n_genes*n_mods, H_shared), all_keys[idx_key])); idx_key+=1
    params['c_shared'] = numpyro.param('c_shared', make('c_shared', (H_shared,), all_keys[idx_key])); idx_key+=1
    # lib embedding
    params['W_lib']    = numpyro.param('W_lib',    make('W_lib',    (1, lib_dim),            all_keys[idx_key])); idx_key+=1
    params['b_lib']    = numpyro.param('b_lib',    make('b_lib',    (lib_dim,),              all_keys[idx_key])); idx_key+=1
    # batch embedding (only if requested)
    if include_batch:
        num_batches = obs2sample.shape[1]
        params['W_batch'] = numpyro.param(
            'W_batch', make('W_batch', (num_batches, batch_dim), all_keys[idx_key])
        ); idx_key += 1
        params['b_batch'] = numpyro.param(
            'b_batch', make('b_batch', (batch_dim,), all_keys[idx_key])
        ); idx_key += 1

    if predict_detection_l_c:
        # ATAC lib embedding
        params["W_lib_atac"] = numpyro.param(
            "W_lib_atac",
            make("W_lib_atac", (1, lib_dim), all_keys[idx_key]),
        )
        idx_key += 1

        params["b_lib_atac"] = numpyro.param(
            "b_lib_atac",
            make("b_lib_atac", (lib_dim,), all_keys[idx_key]),
        )
        idx_key += 1

    # t_c mapping
    params['V_t_c'] = numpyro.param('V_t_c',
        make('V_t_c', (H_aug, hidden_dim), all_keys[idx_key])); idx_key += 1
    params['c_t_c'] = numpyro.param('c_t_c',
        make('c_t_c', (hidden_dim,), all_keys[idx_key])); idx_key += 1

    # optional extra hidden layer
    if use_hidden_layer:
        params['t_c_hidden_W'] = numpyro.param('t_c_hidden_W',
            make('t_c_hidden_W', (H_aug, hidden_dim), all_keys[idx_key])); idx_key += 1
        params['t_c_hidden_b'] = numpyro.param('t_c_hidden_b',
            make('t_c_hidden_b', (hidden_dim,), all_keys[idx_key])); idx_key += 1

    # output mapping (always)
    params['V_out_t_c'] = numpyro.param('V_out_t_c',
        make('V_out_t_c', (hidden_dim, out_dim), all_keys[idx_key])); idx_key += 1
    params['c_out_t_c'] = numpyro.param('c_out_t_c',
        make('c_out_t_c', (out_dim,), all_keys[idx_key])); idx_key += 1

    # detection_y_c mapping (always register the 1-layer head!)
    if predict_detection_y_c:
        # plain 1-layer head
        params['V_det'] = numpyro.param('V_det',
            make('V_det', (H_aug, hidden_dim), all_keys[idx_key])); idx_key += 1
        params['c_det'] = numpyro.param('c_det',
            make('c_det', (hidden_dim,), all_keys[idx_key])); idx_key += 1

        # extra hidden-layer (optional)
        if use_hidden_layer:
            params['det_hidden_W'] = numpyro.param('det_hidden_W',
                make('det_hidden_W', (H_aug, hidden_dim), all_keys[idx_key])); idx_key += 1
            params['det_hidden_b'] = numpyro.param('det_hidden_b',
                make('det_hidden_b', (hidden_dim,), all_keys[idx_key])); idx_key += 1

        # output mapping (always)
        params['V_out_det'] = numpyro.param('V_out_det',
            make('V_out_det', (hidden_dim, out_dim), all_keys[idx_key])); idx_key += 1
        params['c_out_det'] = numpyro.param('c_out_det',
            make('c_out_det', (out_dim,), all_keys[idx_key])); idx_key += 1

    # detection_l_c mapping
    if predict_detection_l_c:
        # always need the "first" Dense for detection_l
        params['V_det_l'] = numpyro.param(
            'V_det_l',
            make('V_det_l', (H_aug, hidden_dim), all_keys[idx_key])
        )
        idx_key += 1

        params['c_det_l'] = numpyro.param(
            'c_det_l',
            make('c_det_l', (hidden_dim,), all_keys[idx_key])
        )
        idx_key += 1

        if use_hidden_layer:
            # extra hidden layer on top
            params['det_l_hidden_W'] = numpyro.param(
                'det_l_hidden_W',
                make('det_l_hidden_W', (hidden_dim, hidden_dim), all_keys[idx_key])
            )
            idx_key += 1

            params['det_l_hidden_b'] = numpyro.param(
                'det_l_hidden_b',
                make('det_l_hidden_b', (hidden_dim,), all_keys[idx_key])
            )
            idx_key += 1

        # output mapping (always)
        params['V_out_det_l'] = numpyro.param(
            'V_out_det_l',
            make('V_out_det_l', (hidden_dim, out_dim), all_keys[idx_key])
        )
        idx_key += 1

        params['c_out_det_l'] = numpyro.param(
            'c_out_det_l',
            make('c_out_det_l', (out_dim,), all_keys[idx_key])
        )
        idx_key += 1

    # ---- path_weights head initialization ----
    if predict_path_weights:
        # hidden‐layer weights
        params['V_pw']     = numpyro.param(
            'V_pw',
            make('V_pw', (H_aug, hidden_dim), all_keys[idx_key])
        ); idx_key += 1
        params['c_pw']     = numpyro.param(
            'c_pw',
            make('c_pw', (hidden_dim,),       all_keys[idx_key])
        ); idx_key += 1

        # output layer projects to 2*num_paths (loc & log‐scale)
        out_dim_pw = 2 * kwargs['num_paths']
        params['V_out_pw'] = numpyro.param(
            'V_out_pw',
            make('V_out_pw', (hidden_dim, out_dim_pw), all_keys[idx_key])
        ); idx_key += 1
        params['c_out_pw'] = numpyro.param(
            'c_out_pw',
            make('c_out_pw', (out_dim_pw,), all_keys[idx_key])
        ); idx_key += 1

    # forward
    batch_input = obs2sample if include_batch else jnp.zeros((n_cells, 0), dtype=jnp.float32)
    outputs = _network_forward(
        params, data_for_forward, batch_input, M_c.reshape((data.shape[0],1)),
        predict_detection_y_c, predict_detection_l_c, predict_path_weights,
        include_batch=include_batch,
        use_hidden_layer = use_hidden_layer, data_atac = data_atac
    )

    # unpack
    idx = 0
    raw_loc, scale_t = outputs[idx], outputs[idx+1]; idx += 2
    loc_t    = T_limits[0] + jax.nn.sigmoid(raw_loc) * (T_limits[1] - T_limits[0])
    dists, names = [dist.Normal(loc_t, scale_t)], ['t_c']

    # detection_y_c
    if predict_detection_y_c:
        loc_y, scale_y = outputs[idx], outputs[idx+1]; idx += 2
        dists.append(dist.TransformedDistribution(dist.Normal(loc_y, scale_y), dist.transforms.ExpTransform())); names.append('detection_y_c')
    # detection_l_c
    if predict_detection_l_c:
        loc_l, scale_l = outputs[idx], outputs[idx+1]; idx += 2
        dists.append(dist.TransformedDistribution(dist.Normal(loc_l, scale_l), dist.transforms.ExpTransform())); names.append('detection_l_c')
    # path_weights
    if predict_path_weights:
        loc_z, scale_z = outputs[idx], outputs[idx+1]
        numpyro.sample('z_pw', dist.Normal(loc_z, scale_z).to_event(1))

    with numpyro.plate('cells', data.shape[0]):
        for nm, sd in zip(names, dists):
            numpyro.sample(nm, sd)

    return {}

def warm_up_guide(
    model,
    model_input: dict,
    predict_detection_l_c: bool = False,
    predict_detection_y_c: bool = True,
    predict_path_weights: bool = False,
    n_steps: int = 1000,
    seed: int = 0,
) -> dict:

    if predict_path_weights is None:
        num_paths = model_input["num_paths"]
    else:
        num_paths = 1

    amortized_fn = partial(
        amortized_guide,
        predict_detection_l_c=predict_detection_l_c,
        predict_detection_y_c=predict_detection_y_c,
        predict_path_weights = predict_path_weights,
        init_net_params=None,
        num_paths= num_paths,
    )

    # --- 1) Define a minimal prior-only model ----------

    def prior_only_tp_model(
        data,  # (n_cells, …)  – unused
        prior_time,  # (n_cells,)
        T_limits,  # (low, high)
        prior_time_sd,  # float
        prior_path,  # (n_cells,)  contains -2 / -1 / ≥0
        num_paths = None,  # int
        obs2sample=None,
        data_atac=None,
        M_c=None
    ):
        n_cells = prior_time.shape[0]

        # Compute relative library size for RNA
        flat   = data.reshape((n_cells, -1))
        M_flat = jnp.squeeze(M_c, axis=(1,2))      # → (n_cells,)
        per_cell = flat / (M_flat[:, None] + 1e-8)
        lib_raw = jnp.sum(per_cell, axis=1)        # → (n_cells,)
        batch_counts = jnp.sum(obs2sample, axis=0)               # (n_batch,)
        batch_sum    = obs2sample.T @ lib_raw                   # (n_batch,)
        batch_mean   = batch_sum / (batch_counts + 1e-8)        # (n_batch,)
        lib_exp = jnp.sum(obs2sample * batch_mean[None, :], axis=1)  # (n_cells,)
        lib_rel = lib_raw / (lib_exp + 1e-8)                     # (n_cells,)

        # Compute relative library size for ATAC
        if data_atac is not None:
            flat_atac = data_atac.reshape((n_cells, -1))
            lib_raw_atac = jnp.sum(flat_atac, axis=1)              # (n_cells,)
            batch_counts = jnp.sum(obs2sample, axis=0)             # (n_batch,)
            batch_sum_atac = obs2sample.T @ lib_raw_atac            # (n_batch,)
            batch_mean_atac = batch_sum_atac / (batch_counts + 1e-8)
            lib_rel_atac = lib_raw_atac / (jnp.sum(obs2sample * batch_mean_atac[None,:], axis=1) + 1e-8)

        # a) Truncated-Normal prior for t_c (exactly as before)
        with numpyro.plate("cells", n_cells):
            numpyro.sample(
                "t_c",
                dist.TruncatedNormal(
                    loc=prior_time,
                    scale=prior_time_sd,
                    low=T_limits[0],
                    high=T_limits[1],
                ),
            )

            α = 100.0
            β = α / lib_rel
            numpyro.sample(
                "detection_y_c",
                dist.Gamma(concentration=α, rate=β),
            )

            if data_atac is not None:
                beta_l = α / lib_rel_atac  # analog of Beta for ATAC
                numpyro.sample(
                    "detection_l_c",
                    dist.Gamma(concentration=α, rate=beta_l),
                )

        if num_paths is not None:
            # b) Logistic-Normal prior for z_pw

            # 1) Build a mask of “known” cells
            known_mask = prior_path >= 0

            # 2) One‐hot encode the known path index (0…num_paths−1). For unknown cells, we ignore this.
            one_hot_known = jax.nn.one_hot(
                jnp.clip(prior_path, 0, num_paths - 1),
                num_paths
            )  # shape = (n_cells, num_paths)

            # 3) Set loc[i] = 3·one_hot_known[i] if cell i is known, else 0-vector
            loc_matrix = jnp.where(
                known_mask[:, None],
                one_hot_known * 3.0,
                jnp.zeros((n_cells, num_paths))
            )

            # 4) Fixed scale = 0.1 for all cells & all paths
            scale_matrix = jnp.ones((n_cells, num_paths)) * 0.1

            # 5) Sample
            numpyro.sample(
                "z_pw",
                dist.Normal(loc=loc_matrix, scale=scale_matrix).to_event(1),
            )

    # --- 2) Extract constants from model_input ---------
    data = model_input["data"]
    prior_time = model_input["prior_time"]
    T_limits = model_input["T_limits"]
    prior_time_sd = model_input["prior_timespan"] / 100.0
    if predict_path_weights:
        prior_path = model_input["prior_path"]
        num_paths = model_input["num_paths"]
    else:
        num_paths = None
        prior_path = None

    if predict_detection_l_c:
        data_atac = model_input["data_atac"]
    else:
        data_atac = None

    # --- 3) SVI setup (same Adam, same Trace_ELBO) ---
    optimizer = optax.adam(learning_rate=1e-3)
    svi = SVI(prior_only_tp_model, amortized_fn, optimizer, loss=Trace_ELBO())

    # --- 4) Initialize SVI state -----------------------
    rng = jax.random.PRNGKey(seed)
    init_rng, _ = jax.random.split(rng)
    state = svi.init(
        init_rng,
        data=data,
        prior_time=prior_time,
        T_limits=T_limits,
        prior_time_sd=prior_time_sd,
        prior_path=prior_path,
        num_paths=num_paths,
        obs2sample=model_input["obs2sample"],
        M_c=model_input["M_c"],
        data_atac = data_atac
    )

    update_fn = jax.jit(lambda st: svi.update(
        st,
        data=data,
        prior_time=prior_time,
        T_limits=T_limits,
        prior_time_sd=prior_time_sd,
        prior_path=prior_path,
        num_paths=num_paths,
        obs2sample=model_input["obs2sample"],
        M_c=model_input["M_c"],
        data_atac = data_atac
    ))

    def run_svi_warmup_local(st):
        def body(carry, _):
            st, _ = carry
            new_st, loss = update_fn(st)
            return (new_st, loss), loss
        (final_state, _), losses = jax.lax.scan(
            body, (st, 0.0), None, length=n_steps
        )
        return final_state, losses

    run_svi_warmup_jit = jax.jit(run_svi_warmup_local)

    # --- 5) Run JIT-compiled warm-up loop ---------------
    state, losses = run_svi_warmup_jit(state)

    # --- 6) Pull out only the NN parameters ------------
    all_params = svi.get_params(state)
    prefixes = (
        # shared trunk + heads
        "V_shared","c_shared",
        "V_t_c","c_t_c","V_out_t_c","c_out_t_c",
        "V_det","c_det","V_out_det","c_out_det",
        "V_det_l","c_det_l","V_out_det_l","c_out_det_l",
        "V_pw","c_pw","V_out_pw","c_out_pw",
        # **side-embeddings**:
        "W_lib","b_lib",
        "W_batch","b_batch",
        "W_lib_atac", "b_lib_atac"
    )

    net_params = {k: v for k, v in all_params.items() if k in prefixes}
    return net_params

# =============================================================================
# 4) Posterior‐mean extraction helpers (updated to call _network_forward)
# =============================================================================

def _select_net_params(params: dict) -> dict:
    """
    Pull out exactly those numpyro.param entries that belong to the amortized
    network (including side-embeddings).
    """
    prefixes = (
        "V_shared", "c_shared",
        "V_t_c", "c_t_c", "V_out_t_c", "c_out_t_c",
        "V_det", "c_det", "V_out_det", "c_out_det",
        "V_det_l", "c_det_l", "V_out_det_l", "c_out_det_l",
        "V_pw", "c_pw", "V_out_pw", "c_out_pw",
        # side-embedding params
        "W_lib", "b_lib",
        "W_lib_atac", "b_lib_atac",
        "W_batch", "b_batch",
    )
    return {k: v for k, v in params.items() if k in prefixes}


def extract_global_posterior_mean(guide, svi_state, svi):
    """
    Extract global latent means from the AutoNormal guide.
    """
    auto = guide._guides[0]
    params = svi.get_params(svi_state)
    return auto.median(params)

def extract_local_posterior_mean(
    guide,
    svi_state,
    svi,
    data: jnp.ndarray,
    obs2sample: jnp.ndarray,
    M_c: jnp.ndarray,
    data_atac: Optional[jnp.ndarray] = None,
    *,
    include_batch: bool = False,
    use_hidden_layer: bool = False,
    num_paths: Optional[int] = None,
):
    params_all = svi.get_params(svi_state)
    net_params = _select_net_params(params_all)

    predict_y = "V_det" in net_params
    predict_l = "V_det_l" in net_params
    predict_pw = "V_pw" in net_params

    M_c_vec = jnp.squeeze(M_c)

    outputs = _network_forward(
        net_params,
        data,
        obs2sample,
        M_c_vec,
        predict_y,
        predict_l,
        predict_pw,
        data_atac=data_atac,
        include_batch=include_batch,
        use_hidden_layer=use_hidden_layer,
    )

    idx = 0
    loc_t, scale_t = outputs[idx], outputs[idx+1]; idx += 2
    result = {"t_c": loc_t}

    if predict_y:
        loc_y, _ = outputs[idx], outputs[idx+1]; idx += 2
        result["detection_y_c"] = jnp.exp(loc_y)

    if predict_l:
        loc_l, _ = outputs[idx], outputs[idx+1]; idx += 2
        result["detection_l_c"] = jnp.exp(loc_l)

    if predict_pw and num_paths is not None:
        loc_z, _ = outputs[idx], outputs[idx+1]
        result["path_weights_full"] = jax.nn.softmax(loc_z, axis=-1)

    return result

def extract_local_means_full(
    guide,
    svi_state,
    svi,
    data_full: jnp.ndarray,
    obs2sample: jnp.ndarray,
    M_c: jnp.ndarray,
    data_atac_full: Optional[jnp.ndarray] = None,
    *,
    batch_size: int = 8192,
    include_batch: bool = False,
    use_hidden_layer: bool = False,
    num_paths: Optional[int] = None,
):
    n_cells = data_full.shape[0]
    params_all = svi.get_params(svi_state)
    net_params = _select_net_params(params_all)

    has_y = "V_det" in net_params
    has_l = "V_det_l" in net_params
    has_pw = "V_pw" in net_params

    M_c_vec = jnp.squeeze(M_c)
    out = {}

    def _store(key, arr, slc):
        if key not in out:
            out[key] = jnp.empty((n_cells, *arr.shape[1:]), dtype=arr.dtype)
        out[key] = out[key].at[slc].set(arr)

    for start in range(0, n_cells, batch_size):
        stop = min(start + batch_size, n_cells)
        batch_rna = data_full[start:stop]
        batch_atac = None if data_atac_full is None else data_atac_full[start:stop]
        obs2_b    = obs2sample[start:stop]
        mc_b      = M_c_vec[start:stop]

        outputs = _network_forward(
            net_params,
            batch_rna,
            obs2_b,
            mc_b,
            has_y,
            has_l,
            has_pw,
            data_atac=batch_atac,
            include_batch=include_batch,
            use_hidden_layer=use_hidden_layer,
        )

        idx = 0
        # t_c
        _store("t_c", outputs[idx], slice(start, stop)); idx += 2

        # detection_y_c
        if has_y:
            _store("detection_y_c", jnp.exp(outputs[idx]), slice(start, stop))
            idx += 2

        # detection_l_c
        if has_l:
            _store("detection_l_c", jnp.exp(outputs[idx]), slice(start, stop))
            idx += 2

        # path_weights
        if has_pw and num_paths is not None:
            pw = jax.nn.softmax(outputs[idx], axis=-1)
            _store("path_weights_full", pw, slice(start, stop))
            idx += 2

    return out

# =============================================================================
# 5) AmortizedNormal helper class (uses the new amortized_guide)
# =============================================================================


class AmortizedNormal:
    def __init__(
        self,
        model,
        predict_detection_y_c: bool = True,
        predict_detection_l_c: bool = False,
        predict_path_weights: bool = False,
        init_net_params: dict = None,
        init_loc_fn=None,
    ):
        self.model = model
        self.predict_detection_l_c = predict_detection_l_c
        self.predict_detection_y_c = predict_detection_y_c
        self.predict_path_weights = predict_path_weights
        self.init_net_params = init_net_params

        # 1) Seed and block any latent sites that the amortized guide will handle
        guided = seed(model, rng_seed=0)
        hide = [
            "K_rh",
            'K_rh_log10',
            "t_c",
            "detection_y_c",
            "T_c",
            "predictions",
            "mu",
            "d_cr",
            "mu_atac",
            "predictions_rearranged",
            "alpha_cg",
            "additive_term",
            "normalizing_term",
            "normalizing_term_atac",
            "P_rh",
            "K_rh_vector",
            "path_weights",
            "sol_at_cells",
            "z_pw",
            "p_model",
            "sigma_tf",
            'p_sim_mean',
            'p_obs_mean',
            "p_sim",
            'init_state_paths'
        ]
        if predict_detection_l_c:
            hide.append("detection_l_c")
        blocked = block(guided, hide=hide)

        # 2) Build a guide list: first an AutoNormal over the blocked model,
        #    then the amortized guide (which now uses JIT).
        self.guide_list = AutoGuideList(model)
        self.guide_list.append(AutoNormal(blocked, init_loc_fn=init_loc_fn))
        self.guide_list.append(
            partial(
                amortized_guide,
                predict_detection_l_c=self.predict_detection_l_c,
                predict_detection_y_c=self.predict_detection_y_c,
                predict_path_weights = self.predict_path_weights,
                init_net_params=self.init_net_params,
            )
        )

    def __call__(self, *args, **kwargs):
        return self.guide_list(*args, **kwargs)

    def sample_posterior(self, *a, **k):
        return self.guide_list.sample_posterior(*a, **k)

    def median(self, *a, **k):
        return self.guide_list.median(*a, **k)

    def quantiles(self, *a, **k):
        return self.guide_list.quantiles(*a, **k)

    def get_posterior(self, *a, **k):
        return self.guide_list.get_posterior(*a, **k)

    def extract_global_means(self, svi_state, svi):
        return extract_global_posterior_mean(self.guide_list, svi_state, svi)

    def extract_local_means(self, svi_state, svi, data, **kw):
        return extract_local_posterior_mean(self.guide_list, svi_state, svi, data, **kw)

    def extract_all_means(
        self,
        svi_state,
        svi,
        data,
        obs2sample,
        M_c,
        *,
        batch_size: int = 1000,
        data_atac = None,
        **kw,
    ):
        global_means = extract_global_posterior_mean(self.guide_list, svi_state, svi)
        local_means = extract_local_means_full(
            self.guide_list,
            svi_state,
            svi,
            data,
            obs2sample,
            M_c,
            batch_size=batch_size,
            data_atac_full = data_atac,
            **kw,
        )
        return global_means, local_means
