from __future__ import annotations

import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from common import DOCS_FIGURES, DOCS_TABLES, RESULTS_FIGURES, RESULTS_TABLES, ensure_dirs
from signatures import SIGNATURES


SCORE_COLUMNS = list(SIGNATURES)


def add_sensitivity_scores(sample_scores: pd.DataFrame) -> pd.DataFrame:
    long_df = sample_scores.melt(
        id_vars=["sample", "patient_id", "tissue_site", "cell_type_clean", "n_cells"],
        value_vars=SCORE_COLUMNS,
        var_name="signature",
        value_name="mean_log_score",
    )

    grouped = long_df.groupby(["cell_type_clean", "signature"], observed=True)["mean_log_score"]
    group_mean = grouped.transform("mean")
    group_std = grouped.transform(lambda values: values.std(ddof=0)).replace(0, np.nan)
    long_df["z_score"] = ((long_df["mean_log_score"] - group_mean) / group_std).fillna(0.0)
    long_df["rank_percentile"] = grouped.transform(lambda values: values.rank(method="average", pct=True))
    return long_df


def summarize_contrast_sensitivity(long_df: pd.DataFrame, contrasts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, contrast in contrasts.iterrows():
        cell_type = contrast["cell_type_clean"]
        signature = contrast["signature"]
        contrast_site = contrast["contrast_site"]
        reference_site = contrast["reference_site"]
        subset = long_df[
            (long_df["cell_type_clean"] == cell_type)
            & (long_df["signature"] == signature)
            & (long_df["tissue_site"].isin([contrast_site, reference_site]))
            & (long_df["n_cells"] >= 20)
        ]
        contrast_values = subset[subset["tissue_site"] == contrast_site]
        reference_values = subset[subset["tissue_site"] == reference_site]
        if contrast_values.empty or reference_values.empty:
            continue
        mean_delta = contrast_values["mean_log_score"].mean() - reference_values["mean_log_score"].mean()
        z_delta = contrast_values["z_score"].mean() - reference_values["z_score"].mean()
        rank_delta = contrast_values["rank_percentile"].mean() - reference_values["rank_percentile"].mean()
        rows.append(
            {
                "cell_type_clean": cell_type,
                "signature": signature,
                "contrast": contrast["contrast"],
                "contrast_site": contrast_site,
                "reference_site": reference_site,
                "original_delta_mean": mean_delta,
                "z_score_delta": z_delta,
                "rank_percentile_delta": rank_delta,
                "original_padj_bh": contrast["padj_bh"],
                "z_score_sign_agrees": np.sign(mean_delta) == np.sign(z_delta),
                "rank_percentile_sign_agrees": np.sign(mean_delta) == np.sign(rank_delta),
            }
        )
    return pd.DataFrame(rows).sort_values(["original_padj_bh", "cell_type_clean", "signature"])


def summarize_signature_correlations(long_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (cell_type, signature), group in long_df.groupby(["cell_type_clean", "signature"], observed=True):
        if group.shape[0] < 3:
            continue
        rows.append(
            {
                "cell_type_clean": cell_type,
                "signature": signature,
                "n_sample_profiles": group.shape[0],
                "pearson_mean_vs_z": group["mean_log_score"].corr(group["z_score"], method="pearson"),
                "spearman_mean_vs_rank": group["mean_log_score"].corr(group["rank_percentile"], method="spearman"),
            }
        )
    return pd.DataFrame(rows).sort_values(["cell_type_clean", "signature"])


def plot_contrast_sensitivity(sensitivity: pd.DataFrame) -> None:
    plot_df = sensitivity.head(14).copy()
    plot_df["label"] = (
        plot_df["contrast_site"].str.replace("_", " ", regex=False)
        + " vs "
        + plot_df["reference_site"].str.replace("_", " ", regex=False)
        + " | "
        + plot_df["cell_type_clean"].str.replace(" cells", "", regex=False)
        + " | "
        + plot_df["signature"].str.replace("_", " ", regex=False).str.title()
    )
    plot_df = plot_df.sort_values("z_score_delta")
    plt.figure(figsize=(11, max(5, 0.42 * len(plot_df))))
    plt.scatter(plot_df["original_delta_mean"], plot_df["label"], label="Original mean-score delta", color="#2c7a76", s=45)
    plt.scatter(plot_df["z_score_delta"], plot_df["label"], label="Z-score delta", color="#8f3d56", s=45)
    plt.axvline(0, color="black", linewidth=0.8)
    plt.xlabel("Contrast effect direction and relative magnitude")
    plt.ylabel("")
    plt.title("Signature contrast sensitivity to score standardization")
    plt.legend(loc="lower right")
    plt.tight_layout()
    for path in [RESULTS_FIGURES / "signature_score_sensitivity.png", DOCS_FIGURES / "signature_score_sensitivity.png"]:
        plt.savefig(path, dpi=300)
    plt.close()


def main() -> None:
    ensure_dirs()
    scores_path = RESULTS_TABLES / "signature_scores_by_sample_celltype.csv"
    contrasts_path = RESULTS_TABLES / "signature_site_contrasts.csv"
    if not scores_path.exists():
        raise FileNotFoundError("Run scripts/04_signature_scoring.py first.")
    if not contrasts_path.exists():
        raise FileNotFoundError("Run scripts/05_signature_statistics.py first.")

    sample_scores = pd.read_csv(scores_path)
    contrasts = pd.read_csv(contrasts_path)
    long_df = add_sensitivity_scores(sample_scores)
    sensitivity = summarize_contrast_sensitivity(long_df, contrasts)
    correlations = summarize_signature_correlations(long_df)

    long_df.to_csv(RESULTS_TABLES / "signature_scores_sensitivity_long.csv", index=False)
    sensitivity.to_csv(RESULTS_TABLES / "signature_contrast_sensitivity.csv", index=False)
    sensitivity.to_csv(DOCS_TABLES / "signature_contrast_sensitivity.csv", index=False)
    correlations.to_csv(RESULTS_TABLES / "signature_score_method_correlations.csv", index=False)
    correlations.to_csv(DOCS_TABLES / "signature_score_method_correlations.csv", index=False)
    plot_contrast_sensitivity(sensitivity)
    print("Wrote signature scoring sensitivity summaries.")


if __name__ == "__main__":
    main()
