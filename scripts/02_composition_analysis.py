from __future__ import annotations

import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from common import DATA_METADATA, DOCS_FIGURES, DOCS_TABLES, RESULTS_FIGURES, RESULTS_TABLES, ensure_dirs


def main() -> None:
    ensure_dirs()
    meta_path = DATA_METADATA / "gse131907_cell_metadata_clean.csv"
    if not meta_path.exists():
        raise FileNotFoundError("Run scripts/01_metadata_overview.py first.")
    meta = pd.read_csv(meta_path, dtype=str)

    counts = (
        meta.groupby(["sample", "patient_id", "tissue_site"], observed=True)
        .size()
        .reset_index(name="n_cells")
        .sort_values(["tissue_site", "sample"])
    )
    counts.to_csv(RESULTS_TABLES / "cell_counts_by_sample.csv", index=False)
    counts.to_csv(DOCS_TABLES / "cell_counts_by_sample.csv", index=False)

    comp = (
        meta.groupby(["sample", "patient_id", "tissue_site", "cell_type_clean"], observed=True)
        .size()
        .reset_index(name="n_cells")
    )
    comp = comp.merge(counts[["sample", "n_cells"]].rename(columns={"n_cells": "total_cells"}), on="sample")
    comp["fraction"] = comp["n_cells"] / comp["total_cells"]
    comp.to_csv(RESULTS_TABLES / "celltype_composition_by_sample.csv", index=False)
    comp.to_csv(DOCS_TABLES / "celltype_composition_by_sample.csv", index=False)

    site_summary = (
        comp.groupby(["tissue_site", "cell_type_clean"], observed=True)["n_cells"]
        .sum()
        .reset_index()
    )
    site_totals = site_summary.groupby("tissue_site", observed=True)["n_cells"].sum().rename("total_cells")
    site_summary = site_summary.merge(site_totals, on="tissue_site")
    site_summary["fraction"] = site_summary["n_cells"] / site_summary["total_cells"]
    site_summary.to_csv(RESULTS_TABLES / "tissue_site_summary.csv", index=False)
    site_summary.to_csv(DOCS_TABLES / "tissue_site_summary.csv", index=False)

    plt.figure(figsize=(10, 4))
    sns.barplot(data=counts, x="sample", y="n_cells", hue="tissue_site", dodge=False)
    plt.xticks(rotation=70, ha="right")
    plt.xlabel("")
    plt.ylabel("Cells")
    plt.tight_layout()
    for path in [RESULTS_FIGURES / "sample_counts_by_tissue.png", DOCS_FIGURES / "sample_counts_by_tissue.png"]:
        plt.savefig(path, dpi=300)
    plt.close()

    top_types = (
        comp.groupby("cell_type_clean", observed=True)["n_cells"]
        .sum()
        .sort_values(ascending=False)
        .head(12)
        .index
    )
    plot_comp = comp[comp["cell_type_clean"].isin(top_types)].copy()
    pivot = plot_comp.pivot_table(
        index="sample",
        columns="cell_type_clean",
        values="fraction",
        fill_value=0,
        observed=True,
    )
    sample_order = counts.sort_values(["tissue_site", "sample"])["sample"]
    pivot = pivot.reindex(sample_order)
    pivot.plot(kind="bar", stacked=True, figsize=(13, 5), width=0.85)
    plt.ylabel("Fraction of cells")
    plt.xlabel("")
    plt.legend(title="Cell type", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    for path in [RESULTS_FIGURES / "celltype_composition_by_sample.png", DOCS_FIGURES / "celltype_composition_by_sample.png"]:
        plt.savefig(path, dpi=300)
    plt.close()

    top_site = site_summary[site_summary["cell_type_clean"].isin(top_types)].copy()
    plt.figure(figsize=(10, 5))
    sns.barplot(data=top_site, x="tissue_site", y="fraction", hue="cell_type_clean")
    plt.xticks(rotation=35, ha="right")
    plt.xlabel("")
    plt.ylabel("Fraction of cells")
    plt.legend(title="Cell type", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    for path in [RESULTS_FIGURES / "top_celltypes_by_site.png", DOCS_FIGURES / "top_celltypes_by_site.png"]:
        plt.savefig(path, dpi=300)
    plt.close()

    print(f"Wrote composition tables and figures for {counts.shape[0]} samples.")


if __name__ == "__main__":
    main()
