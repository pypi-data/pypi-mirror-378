from typing import Dict, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from beartype import beartype
from matplotlib.figure import Figure


@beartype
def plot_auc_metrics(
    auc_results: Dict[str, pd.DataFrame],
    aggregated_results: Dict[str, pd.DataFrame],
) -> Tuple[Figure, Figure]:
    """
    Designed to handle the output of `stormi.evaluation.metrics.auc_metrics` function.
    Plot per-cell-type area under the curve (AUC) metric using seaborn and matplotlib to plot AUC metrics. Each dot is a transcription factor (TF).
    - Area Under the Receiver Operating Curve (AUROC)
    - Area Under the Precision Recall Curve (AUPRC)
    - Ration between AUPRC and percent_pos (AUPRC_lift)
    - Spearman correlation between GRN weight and log(FC) (w_logfc_rho)
    Additionally, plot aggregated metrics.
    - Across TFs per cell type (Per_Cell_Type). Each dot is a cell type.
    - Per TF across cell types (Per_TF). Each dot is a TF.

    Parameters:
    -----------
    auc_results (Dict):
        Per-cell-type results: Keys are cell types; values are DataFrames with AUC statistics.
    grn_dict (dict):
        - Aggregated results: Keys are {"Per_Cell_Type", "Per_TF"}; values are DataFrames with aggregated AUC across cell types or TFs.

    Returns:
    --------
    Tuple[Figure, Figure]:
        A tuple containing two figures:
        - Per-cell-type AUC: Keys are cell types; values are DataFrames with AUC statistics.
        - Aggregated results: Keys are {"Per_Cell_Type", "Per_TF"}; values are DataFrames with aggregated AUC across cell types or TFs.
    """

    # 1) Figure 1: Plot metrics per cell type
    cell_types = auc_results.keys()
    ncols = 4
    nrows = len(cell_types)

    fig1, axes = plt.subplots(
        nrows, ncols, figsize=(4.0 * ncols, 3.2 * nrows), squeeze=False
    )

    for i, ct in enumerate(cell_types):
        df = auc_results[ct]

        # --- Column 0: AUROC ---
        ax = axes[i, 0]
        sns.violinplot(
            data=df,
            y="auroc",
            ax=ax,
            color="dodgerblue",
            inner="box",
            cut=1,
            linewidth=1,
        )
        sns.stripplot(
            data=df, y="auroc", ax=ax, color="black", size=3, jitter=0.15, alpha=1
        )
        ax.set_title("AUROC")
        ax.set_ylim(0, 1)
        ax.axhline(0.5, ls=":", lw=1.2, color="black", alpha=1)
        ax.set_xlabel("")
        ax.set_ylabel(ct, fontsize=12, fontweight="bold", labelpad=10)

        # --- Column 1: AUPRC + baseline ---
        ax = axes[i, 1]
        sns.violinplot(
            data=df, y="auprc", ax=ax, color="orange", inner="box", cut=0, linewidth=1
        )
        sns.stripplot(
            data=df, y="auprc", ax=ax, color="black", size=3, jitter=0.15, alpha=1
        )
        ax.set_title("AUPRC")
        # Baseline = prevalence; here use mean(percent_pos)
        ax.axhline(
            df.percent_pos.mean(),
            color="black",
            linestyle=":",
            linewidth=1.2,
            alpha=0.9,
            label="Baseline\n(mean %pos)",
        )
        # In first column, show legend
        if i == 0:
            ax.legend(frameon=False, loc="upper right")
        ax.set_xlabel("")
        ax.set_ylabel("")

        # --- Column 2: AUPRC lift (AUPRC / prevalence) ---
        ax = axes[i, 2]
        sns.violinplot(
            data=df,
            y="auprc_lift",
            ax=ax,
            color="gold",
            inner="box",
            cut=0,
            linewidth=1,
        )
        sns.stripplot(
            data=df, y="auprc_lift", ax=ax, color="black", size=3, jitter=0.15, alpha=1
        )
        ax.set_title("AUPRC lift")
        ax.set_xlabel("")
        ax.set_ylabel("")

        # --- Column 3: Spearman rho between weight and logFC ---
        ax = axes[i, 3]
        sns.violinplot(
            data=df,
            y="w_logfc_rho",
            ax=ax,
            color="lightgrey",
            inner="box",
            cut=1,
            linewidth=1,
        )
        sns.stripplot(
            data=df, y="w_logfc_rho", ax=ax, color="black", size=3, jitter=0.15, alpha=1
        )
        ax.set_title("rho(Weight, logFC)")
        ax.set_xlabel("")
        ax.set_ylabel("")
        # ax.set_ylim(-1, 1)  # Spearman range

        # Light grid for readability
        for j in range(ncols):
            axes[i, j].grid(axis="y", alpha=0.2)

    fig1.suptitle(
        "Metrics per TFs by cell type", fontsize=15, fontweight="bold", y=0.995
    )

    plt.tight_layout()
    plt.show()

    # 2) Figure 2: Plot aggregated metrics
    fig2, axes = plt.subplots(2, 4, figsize=(16, 6.4), sharey=False)

    for i, m in enumerate(aggregated_results.keys()):
        df = aggregated_results[m]

        # --- Column 0: AUROC ---
        ax = axes[i, 0]
        sns.violinplot(
            data=df,
            y="mean_auroc",
            ax=ax,
            color="dodgerblue",
            inner="box",
            cut=1,
            linewidth=1,
        )
        sns.stripplot(
            data=df, y="mean_auroc", ax=ax, color="black", size=3, jitter=0.15, alpha=1
        )
        ax.set_title("AUROC")
        ax.set_ylim(0, 1)
        ax.set_xlabel("")
        ax.set_ylabel(
            m, fontsize=12, fontweight="bold", labelpad=10
        )  # y-label is the celltype (row label)
        ax.axhline(0.5, ls=":", lw=1.2, color="black", alpha=1)

        # --- Column 1: AUPRC
        ax = axes[i, 1]
        sns.violinplot(
            data=df,
            y="mean_auprc",
            ax=ax,
            color="orange",
            inner="box",
            cut=0,
            linewidth=1,
        )
        sns.stripplot(
            data=df, y="mean_auprc", ax=ax, color="black", size=3, jitter=0.15, alpha=1
        )
        ax.set_title("AUPRC")
        ax.set_xlabel("")
        ax.set_ylabel("")

        # --- Column 2: AUPRC lift ---
        ax = axes[i, 2]
        sns.violinplot(
            data=df,
            y="mean_auprc_lift",
            ax=ax,
            color="gold",
            inner="box",
            cut=0,
            linewidth=1,
        )
        sns.stripplot(
            data=df,
            y="mean_auprc_lift",
            ax=ax,
            color="black",
            size=3,
            jitter=0.15,
            alpha=1,
        )
        ax.set_title("AUPRC lift")
        ax.set_xlabel("")
        ax.set_ylabel("")

        # --- Column 3: Spearman rho between weight and logFC ---
        ax = axes[i, 3]
        sns.violinplot(
            data=df,
            y="mean_rho",
            ax=ax,
            color="lightgrey",
            inner="box",
            cut=1,
            linewidth=1,
        )
        sns.stripplot(
            data=df, y="mean_rho", ax=ax, color="black", size=3, jitter=0.15, alpha=1
        )
        ax.set_title("rho(Weight, logFC)")
        ax.set_xlabel("")
        ax.set_ylabel("")
        # ax.set_ylim(-1, 1)  # Spearman range

        # Light grid for readability
        for j in range(ncols):
            axes[i, j].grid(axis="y", alpha=0.2)

    fig2.suptitle("Aggregated Metrics", fontsize=15, fontweight="bold", y=0.995)

    plt.tight_layout()
    plt.show()

    # 3) Return figures
    return fig1, fig2
