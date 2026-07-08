from __future__ import annotations

import itertools

import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests

from common import DOCS_FIGURES, DOCS_TABLES, RESULTS_FIGURES, RESULTS_TABLES, ensure_dirs


COMPARISONS = [
    {
        "cell_type_clean": "T lymphocytes",
        "reference_site": "normal_lymph_node",
        "contrast_sites": ["primary_tumor", "advanced_airway_tumor", "pleural_effusion"],
        "signatures": ["T_CELL_EXHAUSTION", "CYTOTOXICITY"],
    },
    {
        "cell_type_clean": "Myeloid cells",
        "reference_site": "normal_lymph_node",
        "contrast_sites": ["primary_tumor", "advanced_airway_tumor", "pleural_effusion"],
        "signatures": ["MYELOID_INFLAMMATION", "MACROPHAGE_LIKE"],
    },
    {
        "cell_type_clean": "Epithelial cells",
        "reference_site": "normal_lung",
        "contrast_sites": ["primary_tumor", "advanced_airway_tumor", "pleural_effusion"],
        "signatures": ["EMT_INVASION", "HYPOXIA", "PROLIFERATION"],
    },
]


def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    nx = len(x)
    ny = len(y)
    if nx < 2 or ny < 2:
        return np.nan
    pooled_var = ((nx - 1) * np.var(x, ddof=1) + (ny - 1) * np.var(y, ddof=1)) / (nx + ny - 2)
    if pooled_var <= 0:
        return np.nan
    return (np.mean(x) - np.mean(y)) / np.sqrt(pooled_var)


def run_comparisons(scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for spec in COMPARISONS:
        cell_type = spec["cell_type_clean"]
        reference_site = spec["reference_site"]
        for contrast_site, signature in itertools.product(spec["contrast_sites"], spec["signatures"]):
            ref = scores[
                (scores["cell_type_clean"] == cell_type)
                & (scores["tissue_site"] == reference_site)
                & (scores["n_cells"] >= 20)
            ][signature].dropna()
            contrast = scores[
                (scores["cell_type_clean"] == cell_type)
                & (scores["tissue_site"] == contrast_site)
                & (scores["n_cells"] >= 20)
            ][signature].dropna()
            if len(ref) >= 3 and len(contrast) >= 3:
                stat, pvalue = stats.mannwhitneyu(contrast, ref, alternative="two-sided")
            else:
                stat, pvalue = np.nan, np.nan
            rows.append(
                {
                    "cell_type_clean": cell_type,
                    "signature": signature,
                    "contrast": f"{contrast_site}_vs_{reference_site}",
                    "contrast_site": contrast_site,
                    "reference_site": reference_site,
                    "n_contrast_samples": len(contrast),
                    "n_reference_samples": len(ref),
                    "mean_contrast": float(np.mean(contrast)) if len(contrast) else np.nan,
                    "mean_reference": float(np.mean(ref)) if len(ref) else np.nan,
                    "delta_mean": float(np.mean(contrast) - np.mean(ref)) if len(contrast) and len(ref) else np.nan,
                    "cohens_d": cohens_d(contrast.to_numpy(), ref.to_numpy()) if len(contrast) and len(ref) else np.nan,
                    "mannwhitney_u": stat,
                    "pvalue": pvalue,
                }
            )
    out = pd.DataFrame(rows)
    valid = out["pvalue"].notna()
    out["padj_bh"] = np.nan
    if valid.any():
        out.loc[valid, "padj_bh"] = multipletests(out.loc[valid, "pvalue"], method="fdr_bh")[1]
    return out.sort_values(["padj_bh", "pvalue", "cell_type_clean", "signature"], na_position="last")


def plot_effects(stats_df: pd.DataFrame) -> None:
    plot_df = (
        stats_df.dropna(subset=["delta_mean"])
        .assign(abs_delta=lambda df: df["delta_mean"].abs())
        .sort_values(["padj_bh", "abs_delta"], ascending=[True, False])
        .head(14)
        .copy()
    )
    plot_df["label"] = (
        plot_df["contrast_site"].str.replace("_", " ", regex=False)
        + " vs "
        + plot_df["reference_site"].str.replace("_", " ", regex=False)
        + " | "
        + plot_df["cell_type_clean"].str.replace(" cells", "", regex=False)
        + " | "
        + plot_df["signature"].str.replace("_", " ", regex=False).str.title()
    )
    plot_df = plot_df.sort_values("delta_mean")
    plt.figure(figsize=(11, max(5, 0.42 * len(plot_df))))
    colors = ["#9c3f3f" if value < 0 else "#24746f" for value in plot_df["delta_mean"]]
    plt.barh(plot_df["label"], plot_df["delta_mean"], color=colors)
    plt.axvline(0, color="black", linewidth=0.8)
    plt.xlabel("Mean signature score difference")
    plt.ylabel("")
    plt.title("Top sample-level TME signature differences")
    plt.tight_layout()
    for path in [RESULTS_FIGURES / "signature_contrast_effect_sizes.png", DOCS_FIGURES / "signature_contrast_effect_sizes.png"]:
        plt.savefig(path, dpi=300)
    plt.close()


def main() -> None:
    ensure_dirs()
    scores_path = RESULTS_TABLES / "signature_scores_by_sample_celltype.csv"
    if not scores_path.exists():
        raise FileNotFoundError("Run scripts/04_signature_scoring.py first.")
    scores = pd.read_csv(scores_path)
    stats_df = run_comparisons(scores)
    stats_df.to_csv(RESULTS_TABLES / "signature_site_contrasts.csv", index=False)
    stats_df.to_csv(DOCS_TABLES / "signature_site_contrasts.csv", index=False)
    plot_effects(stats_df)
    print("Wrote sample-level signature contrast statistics.")


if __name__ == "__main__":
    main()
