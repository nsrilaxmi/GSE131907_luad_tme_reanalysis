from __future__ import annotations

import itertools

import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from common import DOCS_FIGURES, DOCS_TABLES, RESULTS_FIGURES, RESULTS_TABLES, ensure_dirs


PAIRED_COMPARISONS = [
    {
        "cell_type_clean": "T lymphocytes",
        "reference_site": "normal_lymph_node",
        "contrast_sites": ["advanced_airway_tumor", "pleural_effusion"],
        "signatures": ["T_CELL_EXHAUSTION", "CYTOTOXICITY"],
    },
    {
        "cell_type_clean": "Myeloid cells",
        "reference_site": "normal_lymph_node",
        "contrast_sites": ["advanced_airway_tumor", "pleural_effusion"],
        "signatures": ["MYELOID_INFLAMMATION", "MACROPHAGE_LIKE"],
    },
    {
        "cell_type_clean": "Epithelial cells",
        "reference_site": "normal_lung",
        "contrast_sites": ["primary_tumor", "advanced_airway_tumor"],
        "signatures": ["EMT_INVASION", "HYPOXIA", "PROLIFERATION"],
    },
]


def paired_contrasts(scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    scores = scores[scores["n_cells"] >= 20].copy()
    patient_scores = (
        scores.groupby(["patient_id", "tissue_site", "cell_type_clean"], observed=True)
        .mean(numeric_only=True)
        .reset_index()
    )

    for spec in PAIRED_COMPARISONS:
        cell_type = spec["cell_type_clean"]
        reference_site = spec["reference_site"]
        for contrast_site, signature in itertools.product(spec["contrast_sites"], spec["signatures"]):
            subset = patient_scores[
                (patient_scores["cell_type_clean"] == cell_type)
                & (patient_scores["tissue_site"].isin([reference_site, contrast_site]))
            ]
            wide = subset.pivot_table(index="patient_id", columns="tissue_site", values=signature, observed=True)
            if reference_site not in wide or contrast_site not in wide:
                paired = pd.DataFrame(columns=[reference_site, contrast_site])
            else:
                paired = wide[[reference_site, contrast_site]].dropna()
            deltas = paired[contrast_site] - paired[reference_site] if not paired.empty else pd.Series(dtype=float)
            if len(deltas) >= 3 and not np.allclose(deltas, 0):
                stat, pvalue = stats.wilcoxon(deltas, alternative="two-sided", zero_method="wilcox")
            else:
                stat, pvalue = np.nan, np.nan
            rows.append(
                {
                    "cell_type_clean": cell_type,
                    "signature": signature,
                    "contrast": f"{contrast_site}_vs_{reference_site}",
                    "contrast_site": contrast_site,
                    "reference_site": reference_site,
                    "n_paired_patients": len(deltas),
                    "mean_paired_delta": float(deltas.mean()) if len(deltas) else np.nan,
                    "median_paired_delta": float(deltas.median()) if len(deltas) else np.nan,
                    "wilcoxon_statistic": stat,
                    "pvalue": pvalue,
                    "paired_patient_ids": ";".join(map(str, paired.index.tolist())) if len(deltas) else "",
                }
            )

    out = pd.DataFrame(rows)
    valid = out["pvalue"].notna()
    out["padj_bh"] = np.nan
    if valid.any():
        out.loc[valid, "padj_bh"] = multipletests(out.loc[valid, "pvalue"], method="fdr_bh")[1]
    return out.sort_values(["n_paired_patients", "padj_bh", "cell_type_clean", "signature"], ascending=[False, True, True, True])


def plot_paired_deltas(stats_df: pd.DataFrame) -> None:
    plot_df = (
        stats_df.dropna(subset=["mean_paired_delta"])
        .sort_values(["n_paired_patients", "mean_paired_delta"], ascending=[False, False])
        .head(14)
        .copy()
    )
    if plot_df.empty:
        return
    plot_df["label"] = (
        plot_df["contrast_site"].str.replace("_", " ", regex=False)
        + " vs "
        + plot_df["reference_site"].str.replace("_", " ", regex=False)
        + " | "
        + plot_df["cell_type_clean"].str.replace(" cells", "", regex=False)
        + " | "
        + plot_df["signature"].str.replace("_", " ", regex=False).str.title()
        + " (n="
        + plot_df["n_paired_patients"].astype(str)
        + ")"
    )
    plot_df = plot_df.sort_values("mean_paired_delta")
    colors = ["#8f3d56" if value < 0 else "#2c7a76" for value in plot_df["mean_paired_delta"]]

    plt.figure(figsize=(11, max(5, 0.45 * len(plot_df))))
    plt.barh(plot_df["label"], plot_df["mean_paired_delta"], color=colors)
    plt.axvline(0, color="black", linewidth=0.8)
    plt.xlabel("Mean within-patient signature score difference")
    plt.ylabel("")
    plt.title("Paired patient TME signature contrasts")
    plt.tight_layout()
    for path in [RESULTS_FIGURES / "paired_patient_signature_deltas.png", DOCS_FIGURES / "paired_patient_signature_deltas.png"]:
        plt.savefig(path, dpi=300)
    plt.close()


def main() -> None:
    ensure_dirs()
    scores_path = RESULTS_TABLES / "signature_scores_by_sample_celltype.csv"
    if not scores_path.exists():
        raise FileNotFoundError("Run scripts/04_signature_scoring.py first.")
    scores = pd.read_csv(scores_path)
    stats_df = paired_contrasts(scores)
    stats_df.to_csv(RESULTS_TABLES / "paired_patient_signature_contrasts.csv", index=False)
    stats_df.to_csv(DOCS_TABLES / "paired_patient_signature_contrasts.csv", index=False)
    plot_paired_deltas(stats_df)
    print("Wrote paired patient signature contrast summaries.")


if __name__ == "__main__":
    main()
