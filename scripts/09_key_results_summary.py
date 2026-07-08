from __future__ import annotations

import pandas as pd

from common import DOCS_TABLES, RESULTS_TABLES, ensure_dirs


KEY_SAMPLE_CONTRASTS = [
    ("Epithelial cells", "HYPOXIA", "advanced_airway_tumor_vs_normal_lung"),
    ("Epithelial cells", "PROLIFERATION", "advanced_airway_tumor_vs_normal_lung"),
    ("Myeloid cells", "MYELOID_INFLAMMATION", "primary_tumor_vs_normal_lymph_node"),
    ("Myeloid cells", "MACROPHAGE_LIKE", "primary_tumor_vs_normal_lymph_node"),
    ("T lymphocytes", "CYTOTOXICITY", "advanced_airway_tumor_vs_normal_lymph_node"),
    ("T lymphocytes", "T_CELL_EXHAUSTION", "primary_tumor_vs_normal_lymph_node"),
]


KEY_PAIRED_CONTRASTS = [
    ("Epithelial cells", "HYPOXIA", "primary_tumor_vs_normal_lung"),
]


def clean_label(value: str) -> str:
    return str(value).replace("_", " ")


def summarize_sample_contrasts(sample_stats: pd.DataFrame) -> list[dict]:
    rows = []
    for cell_type, signature, contrast in KEY_SAMPLE_CONTRASTS:
        match = sample_stats[
            (sample_stats["cell_type_clean"] == cell_type)
            & (sample_stats["signature"] == signature)
            & (sample_stats["contrast"] == contrast)
        ]
        if match.empty:
            continue
        item = match.iloc[0]
        rows.append(
            {
                "result_type": "sample_level_contrast",
                "cell_type": cell_type,
                "signature": signature,
                "comparison": f"{clean_label(item['contrast_site'])} vs {clean_label(item['reference_site'])}",
                "n": f"{int(item['n_contrast_samples'])} vs {int(item['n_reference_samples'])} samples",
                "effect": item["delta_mean"],
                "effect_label": "mean score difference",
                "padj_bh": item["padj_bh"],
                "interpretation": (
                    f"{clean_label(signature).title()} is higher in {clean_label(item['contrast_site'])} "
                    f"than {clean_label(item['reference_site'])} within {cell_type.lower()}."
                ),
            }
        )
    return rows


def summarize_paired_contrasts(paired_stats: pd.DataFrame) -> list[dict]:
    rows = []
    for cell_type, signature, contrast in KEY_PAIRED_CONTRASTS:
        match = paired_stats[
            (paired_stats["cell_type_clean"] == cell_type)
            & (paired_stats["signature"] == signature)
            & (paired_stats["contrast"] == contrast)
        ]
        if match.empty:
            continue
        item = match.iloc[0]
        rows.append(
            {
                "result_type": "paired_patient_contrast",
                "cell_type": cell_type,
                "signature": signature,
                "comparison": f"{clean_label(item['contrast_site'])} vs {clean_label(item['reference_site'])}",
                "n": f"{int(item['n_paired_patients'])} paired patients",
                "effect": item["mean_paired_delta"],
                "effect_label": "mean within-patient score difference",
                "padj_bh": item["padj_bh"],
                "interpretation": (
                    f"{clean_label(signature).title()} is higher in {clean_label(item['contrast_site'])} "
                    f"than matched {clean_label(item['reference_site'])} within {cell_type.lower()}."
                ),
            }
        )
    return rows


def main() -> None:
    ensure_dirs()
    sample_path = RESULTS_TABLES / "signature_site_contrasts.csv"
    paired_path = RESULTS_TABLES / "paired_patient_signature_contrasts.csv"
    if not sample_path.exists():
        raise FileNotFoundError("Run scripts/05_signature_statistics.py first.")
    if not paired_path.exists():
        raise FileNotFoundError("Run scripts/07_paired_patient_analysis.py first.")

    sample_stats = pd.read_csv(sample_path)
    paired_stats = pd.read_csv(paired_path)
    rows = summarize_paired_contrasts(paired_stats) + summarize_sample_contrasts(sample_stats)
    out = pd.DataFrame(rows).sort_values(["result_type", "padj_bh", "signature"])
    out.to_csv(RESULTS_TABLES / "key_results_summary.csv", index=False)
    out.to_csv(DOCS_TABLES / "key_results_summary.csv", index=False)
    print("Wrote key results summary table.")


if __name__ == "__main__":
    main()
