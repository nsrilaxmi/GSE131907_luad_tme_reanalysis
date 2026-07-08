from __future__ import annotations

import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from common import DATA_METADATA, DOCS_FIGURES, DOCS_TABLES, RESULTS_FIGURES, RESULTS_TABLES, ensure_dirs
from signatures import SIGNATURES


MIN_SAMPLE_SUBTYPE_CELLS = 20
MIN_TOTAL_SUBTYPE_CELLS = 400


def clean_label(value: str) -> str:
    return str(value).replace("_", " ")


def write_composition(meta: pd.DataFrame) -> pd.DataFrame:
    sample_totals = (
        meta.groupby(["sample", "patient_id", "tissue_site"], observed=True)
        .size()
        .reset_index(name="total_cells")
    )
    subtype_comp = (
        meta.groupby(["sample", "patient_id", "tissue_site", "cell_type_clean", "Cell_subtype"], observed=True)
        .size()
        .reset_index(name="n_cells")
        .merge(sample_totals, on=["sample", "patient_id", "tissue_site"], how="left")
    )
    subtype_comp["sample_fraction"] = subtype_comp["n_cells"] / subtype_comp["total_cells"]
    subtype_comp.to_csv(RESULTS_TABLES / "subtype_composition_by_sample.csv", index=False)
    subtype_comp.to_csv(DOCS_TABLES / "subtype_composition_by_sample.csv", index=False)

    tissue_comp = (
        subtype_comp.groupby(["tissue_site", "cell_type_clean", "Cell_subtype"], observed=True)["n_cells"]
        .sum()
        .reset_index()
    )
    tissue_totals = tissue_comp.groupby("tissue_site", observed=True)["n_cells"].sum().rename("total_cells")
    tissue_comp = tissue_comp.merge(tissue_totals, on="tissue_site", how="left")
    tissue_comp["fraction"] = tissue_comp["n_cells"] / tissue_comp["total_cells"]
    tissue_comp.to_csv(RESULTS_TABLES / "subtype_composition_by_tissue.csv", index=False)
    tissue_comp.to_csv(DOCS_TABLES / "subtype_composition_by_tissue.csv", index=False)
    return tissue_comp


def plot_top_subtypes(tissue_comp: pd.DataFrame) -> None:
    top_subtypes = (
        tissue_comp.groupby("Cell_subtype", observed=True)["n_cells"]
        .sum()
        .sort_values(ascending=False)
        .head(16)
        .index
    )
    plot_df = tissue_comp[tissue_comp["Cell_subtype"].isin(top_subtypes)].copy()
    plot_df["tissue_site"] = plot_df["tissue_site"].map(clean_label)
    plt.figure(figsize=(11, 5.5))
    sns.barplot(data=plot_df, x="tissue_site", y="fraction", hue="Cell_subtype")
    plt.xticks(rotation=30, ha="right")
    plt.xlabel("")
    plt.ylabel("Fraction of annotated cells")
    plt.title("Most abundant cell subtypes by tissue site")
    plt.legend(title="Cell subtype", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    for path in [RESULTS_FIGURES / "top_subtypes_by_tissue.png", DOCS_FIGURES / "top_subtypes_by_tissue.png"]:
        plt.savefig(path, dpi=300)
    plt.close()


def summarize_subtype_scores(cell_scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    score_cols = list(SIGNATURES)
    sample_scores = (
        cell_scores.groupby(["sample", "patient_id", "tissue_site", "cell_type_clean", "Cell_subtype"], observed=True)
        .agg(n_cells=("Index", "size"), **{col: (col, "mean") for col in score_cols})
        .reset_index()
    )
    sample_scores.to_csv(RESULTS_TABLES / "signature_scores_by_sample_subtype.csv", index=False)
    sample_scores.to_csv(DOCS_TABLES / "signature_scores_by_sample_subtype.csv", index=False)

    filtered = sample_scores[sample_scores["n_cells"] >= MIN_SAMPLE_SUBTYPE_CELLS].copy()
    tissue_scores = (
        filtered.groupby(["tissue_site", "cell_type_clean", "Cell_subtype"], observed=True)
        .agg(
            total_cells=("n_cells", "sum"),
            n_sample_subtypes=("n_cells", "size"),
            mean_cells_per_sample=("n_cells", "mean"),
            **{col: (col, "mean") for col in score_cols},
        )
        .reset_index()
    )
    tissue_scores.to_csv(RESULTS_TABLES / "signature_scores_by_tissue_subtype.csv", index=False)
    tissue_scores.to_csv(DOCS_TABLES / "signature_scores_by_tissue_subtype.csv", index=False)
    return sample_scores, tissue_scores


def plot_signature_heatmap(tissue_scores: pd.DataFrame, cell_type: str, signatures: list[str], filename: str, title: str) -> None:
    subset = tissue_scores[tissue_scores["cell_type_clean"] == cell_type].copy()
    if subset.empty:
        return
    subtype_totals = subset.groupby("Cell_subtype", observed=True)["total_cells"].sum()
    keep = subtype_totals[subtype_totals >= MIN_TOTAL_SUBTYPE_CELLS].index
    subset = subset[subset["Cell_subtype"].isin(keep)].copy()
    if subset.empty:
        return
    subset["label"] = subset["tissue_site"].map(clean_label) + " | " + subset["Cell_subtype"].astype(str)
    matrix = subset.set_index("label")[signatures].sort_index()

    plt.figure(figsize=(7.5, max(4.5, 0.30 * len(matrix))))
    sns.heatmap(matrix, cmap="mako", linewidths=0.2, cbar_kws={"label": "Mean signature score"})
    plt.xlabel("")
    plt.ylabel("")
    plt.title(title)
    plt.tight_layout()
    for path in [RESULTS_FIGURES / filename, DOCS_FIGURES / filename]:
        plt.savefig(path, dpi=300)
    plt.close()


def main() -> None:
    ensure_dirs()
    metadata_path = DATA_METADATA / "gse131907_cell_metadata_clean.csv"
    scores_path = RESULTS_TABLES / "cell_signature_scores_selected_genes.csv"
    if not metadata_path.exists():
        raise FileNotFoundError("Run scripts/01_metadata_overview.py first.")
    if not scores_path.exists():
        raise FileNotFoundError("Run scripts/04_signature_scoring.py first.")

    meta = pd.read_csv(metadata_path, dtype=str)
    tissue_comp = write_composition(meta)
    plot_top_subtypes(tissue_comp)

    cell_scores = pd.read_csv(scores_path)
    _, tissue_scores = summarize_subtype_scores(cell_scores)
    plot_signature_heatmap(
        tissue_scores,
        "T lymphocytes",
        ["T_CELL_EXHAUSTION", "CYTOTOXICITY"],
        "tcell_subtype_signature_heatmap.png",
        "T-cell subtype signature scores",
    )
    plot_signature_heatmap(
        tissue_scores,
        "Myeloid cells",
        ["MYELOID_INFLAMMATION", "MACROPHAGE_LIKE"],
        "myeloid_subtype_signature_heatmap.png",
        "Myeloid subtype signature scores",
    )
    plot_signature_heatmap(
        tissue_scores,
        "Epithelial cells",
        ["EMT_INVASION", "HYPOXIA", "PROLIFERATION"],
        "epithelial_subtype_signature_heatmap.png",
        "Epithelial subtype signature scores",
    )
    print("Wrote subtype composition and subtype-level signature summaries.")


if __name__ == "__main__":
    main()
