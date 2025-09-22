import warnings
from typing import Dict, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd
from beartype import beartype
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score, roc_auc_score


@beartype
def auc_metrics(
    degs: pd.DataFrame,
    grn_dict: dict,
    sign: Literal[None, "pos", "neg"] = None,
    cell_types: Optional[List[str]] = None,
    custom_tfs: Optional[List[str]] = None,
    custom_genes: Optional[List[str]] = None,
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """
    Compute per-cell-type area under the curve (AUC) metrics using sklearn and scipy. Within each cell type, every metric is computed for each transcription factor (TF).
        - Area Under the Receiver Operating Curve (AUROC)
        - Area Under the Precision Recall Curve (AUPRC)
        - Prevalence of ground truth positives (percent_pos)
        - Ration between AUPRC and percent_pos (AUPRC_lift)
        - Spearman correlation between GRN weight and log(FC) (w_logfc_rho)
    Ground truth positives are defined as TF-gene connections where p-val < 0.5 and absolute log(FC) > 0.5.
    Additionally, compute aggregated metrics using the mean.
        - Across TFs per cell type (Per_Cell_Type). Each row is a cell type.
        - Per TF across cell types (Per_TF). Each row is a TF.

    Parameters:
    -----------
    degs (pd.DataFrame):
        A dataframe containing the results of DGEA on CRISPR/Cas9 perturbation screens.
        Must contain the following columns: "crispr_target", "DEG" (differentially expressed gene names), “pvals_adj" (adjusted p-value for each DEG), "logfoldchanges", "celltypes".
    grn_dict (dict):
        Dictionary containing GRNs with keys matching "celltypes" column values in `degs`.
    sign : {"None", "pos", "neg"}, default="None"
        Nature of regulation to consider:
        - "None": disregard sign of edge weights in grn and log(FC) in DGEA
        - "pos": only compare positive weights to negative log(FC)
        - "neg": only compare negative weights to positive log(FC)
    cell_types (list): optional
        List containing custom subset of celltype names in `degs` and `grn_dict`.
    custom_tfs (list): optional
        List containing custom subset of transcription factor names to consider when intersecting TFs from `degs` and `grn_dict`.
    custom_genes (list): optional
        List containing custom subset of gene names to consider when intersecting genes from `degs` and `grn_dict`.

    Returns:
    --------
    Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
        A tuple containing two dictionaries:
        - Per-cell-type results: Keys are cell types; values are DataFrames with AUC statistics.
        - Aggregated results: Keys are {"Per_Cell_Type", "Per_TF"}; values are DataFrames with aggregated AUC across cell types or TFs.
    """

    # 1) List of cell types in this analysis. If not specified, use all cell types
    if cell_types is None:
        cell_types = grn_dict.keys()

    # 2) Big For loop over cell types
    auc_results_dict = {}
    auc_agg_dict = {}

    for ct in cell_types:
        # 2.1) Subset data to cell type
        degs_ct = degs[degs["celltypes"] == ct].copy()
        grn_ct = grn_dict[ct].copy()

        # 2.2) Reformat GRN - One column for regulator, target, and weight respectively
        grn_ct = (
            grn_ct.replace(0, np.nan)
            .stack()
            .reset_index(name="weight")
            .rename(columns={"level_0": "regulator", "level_1": "target"})
        )

        # 2.3) Subset by sign if specified
        if sign == "pos":  # Positive weights, negative log(FC)
            grn_ct = grn_ct[grn_ct.weight >= 0].copy()
            degs_ct = degs_ct[degs_ct.logfoldchanges <= 0].copy()
        elif sign == "neg":  # Negative weights, positive log(FC)
            grn_ct = grn_ct[grn_ct.weight <= 0].copy()
            degs_ct = degs_ct[degs_ct.logfoldchanges >= 0].copy()

        # 2.4) Subset data to TF-gene connections present in both degs and regs
        tf_intersection = set(degs_ct.crispr_target).intersection(grn_ct.regulator)
        if custom_tfs is not None:
            tf_intersection = tf_intersection.intersection(custom_tfs)
        print(f"{ct}\n\tTF intersection: {len(tf_intersection)}")

        gene_intersection = set(degs_ct.DEG).intersection(grn_ct.target)
        if custom_genes is not None:
            gene_intersection = gene_intersection.intersection(custom_genes)
        print(f"\tGene intersection: {len(gene_intersection)}")

        degs_ct = degs_ct[
            degs_ct.crispr_target.isin(tf_intersection)
            & degs_ct.DEG.isin(gene_intersection)
        ].copy()
        grn_ct = grn_ct[
            grn_ct.regulator.isin(tf_intersection)
            & grn_ct.target.isin(gene_intersection)
        ].copy()
        # Skip cell type if empty tf or gene intersection
        if len(tf_intersection) == 0 or len(gene_intersection) == 0:
            print("\tZero TFs or genes left. Will be skipped in AUC analysis")
            continue

        # 2.5) Add ground truth labels to degs. p-val < 0.05 & ab(log(FC)) > 0.5. (1, 0)
        degs_ct["ground_truth"] = (
            (degs_ct.pvals_adj < 0.05) & (degs_ct.logfoldchanges.abs() > 0.5)
        ).astype(int)

        # 2.6) Merge degs and regs
        degs_ct = (
            degs_ct.rename(columns={"crispr_target": "regulator", "DEG": "target"})
            .loc[
                :,
                ["regulator", "target", "logfoldchanges", "pvals_adj", "ground_truth"],
            ]
            .copy()
        )
        auc_df_ct = degs_ct.merge(grn_ct, on=["regulator", "target"], how="left")
        auc_df_ct.weight = auc_df_ct.weight.fillna(0)

        # 2.7) Perform AUROC and AUPRC for each TF
        results_df_ct = list()

        for tf in auc_df_ct.regulator.unique():
            # Extract TF-specific ground truth, weights and log(FC)
            y_true = auc_df_ct[auc_df_ct.regulator.eq(tf)].ground_truth
            y_score = auc_df_ct[auc_df_ct.regulator.eq(tf)]["weight"].abs()
            logfc = auc_df_ct[auc_df_ct.regulator.eq(tf)]["logfoldchanges"].abs()

            # AUROC (Suppress warning that y_true only has one class (when there are no significant DEGs)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                auroc = roc_auc_score(y_true, y_score)
            # AUPRC
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                auprc = average_precision_score(y_true, y_score)

            # Number of significant DEGs, percent of ground truth positives (baseline for AUPRC), and non-zero edges in GRN for the given tf
            n_degs = sum(y_true)
            percent_pos = n_degs / len(y_true)
            n_edges = sum(y_score != 0)

            # Spearman rho between weights and log(FC)
            rho, _ = spearmanr(y_score, logfc)

            # Add to dictionary
            results_df_ct.append(
                {
                    "regulator": tf,
                    "auroc": auroc,
                    "auprc": auprc,
                    "w_logfc_rho": rho,
                    "percent_pos": percent_pos,
                    "n_degs": n_degs,
                    "n_edges": n_edges,
                }
            )

        # 2.8) Add additional metrics
        results_df_ct = pd.DataFrame(results_df_ct)
        results_df_ct["auprc_gain"] = (
            results_df_ct["auprc"] - results_df_ct["percent_pos"]
        ) / (1 - results_df_ct["percent_pos"])
        results_df_ct["auprc_lift"] = (
            results_df_ct["auprc"] / results_df_ct["percent_pos"]
        )

        # 2.9) Append to output dictionary
        auc_results_dict[ct] = results_df_ct

    # 3) Aggregated metrics
    # 3.1) Across TFs per cell type
    df_list = []

    for ct in auc_results_dict.keys():
        df_ct = auc_results_dict[ct]
        # aggregated metric per cell type using the mean
        agg_dict_ct = {
            "n_tfs": df_ct.shape[0],
            "mean_auroc": df_ct.auroc.mean(),
            "n_auroc_na": df_ct.auroc.isna().sum(),
            "mean_auprc": df_ct.auprc.mean(),
            "mean_auprc_lift": df_ct.auprc_lift.mean(),
            "mean_rho": df_ct.w_logfc_rho.mean(),
        }
        df_list.append(agg_dict_ct)

    agg_df = pd.DataFrame(df_list)
    agg_df.index = auc_results_dict.keys()
    # Append aggregated df to output dictionary
    auc_agg_dict["Per_Cell_Type"] = agg_df

    # 3.2) Per TF across cell types
    # Get union of Tfs across cell types
    all_tfs = sorted(set().union(*[df.regulator for df in auc_results_dict.values()]))
    columns = ["auroc", "auprc", "auprc_lift", "w_logfc_rho"]
    # List of reindexed dataframes
    aligned = [
        df.set_index("regulator").reindex(index=all_tfs, columns=columns)
        for df in auc_results_dict.values()
    ]
    # Number of NaNs from abence of positives (DEGs) for TF or absence of TF in the cell type GRN
    n_nan = pd.concat([df.auroc.isna().astype(int) for df in aligned], axis=1).sum(
        axis=1
    )
    # Stack to 3D numpy array
    stacked = np.stack([df.values for df in aligned])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mean_df = pd.DataFrame(
            index=all_tfs, columns=columns, data=np.nanmean(stacked, axis=0)
        )
    # Rename columns and add NaN count
    mean_df = mean_df.rename(
        columns={
            "auroc": "mean_auroc",
            "auprc": "mean_auprc",
            "auprc_lift": "mean_auprc_lift",
            "w_logfc_rho": "mean_rho",
        }
    )
    mean_df["n_nan"] = n_nan
    # Append aggregated df to output dictionary
    auc_agg_dict["Per_TF"] = mean_df

    # 8) Return results
    return auc_results_dict, auc_agg_dict
