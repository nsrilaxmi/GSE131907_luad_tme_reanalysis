from __future__ import annotations

import gzip
from collections import defaultdict

import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from common import DATA_METADATA, DATA_RAW, DOCS_FIGURES, DOCS_TABLES, RESULTS_FIGURES, RESULTS_TABLES, ensure_dirs, load_config
from signatures import SIGNATURES


def read_header(matrix_path):
    with gzip.open(matrix_path, "rt") as handle:
        header = handle.readline().rstrip("\n").split("\t")
    if header[0] != "Index":
        raise ValueError(f"Unexpected first matrix column: {header[0]}")
    return header[1:]


def compute_library_sizes(matrix_path, n_cells: int) -> np.ndarray:
    library = np.zeros(n_cells, dtype=np.float64)
    with gzip.open(matrix_path, "rt") as handle:
        handle.readline()
        for i, line in enumerate(handle, start=1):
            tab = line.find("\t")
            if tab < 0:
                continue
            values = np.fromstring(line[tab + 1 :], sep="\t", dtype=np.float64)
            if values.size != n_cells:
                raise ValueError(f"Line {i} has {values.size} values; expected {n_cells}.")
            library += values
            if i % 5000 == 0:
                print(f"Library-size pass: processed {i} genes")
    return library


def score_signatures(matrix_path, library: np.ndarray) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    gene_to_signatures = defaultdict(list)
    for signature, genes in SIGNATURES.items():
        for gene in genes:
            gene_to_signatures[gene].append(signature)

    n_cells = library.size
    accum = {signature: np.zeros(n_cells, dtype=np.float32) for signature in SIGNATURES}
    counts = {signature: 0 for signature in SIGNATURES}
    found = {signature: [] for signature in SIGNATURES}
    safe_library = np.maximum(library, 1.0)

    with gzip.open(matrix_path, "rt") as handle:
        handle.readline()
        for i, line in enumerate(handle, start=1):
            tab = line.find("\t")
            if tab < 0:
                continue
            gene = line[:tab]
            if gene not in gene_to_signatures:
                continue
            values = np.fromstring(line[tab + 1 :], sep="\t", dtype=np.float32)
            normalized = np.log1p((values / safe_library) * 1e4).astype(np.float32)
            for signature in gene_to_signatures[gene]:
                accum[signature] += normalized
                counts[signature] += 1
                found[signature].append(gene)
            print(f"Signature pass: captured {gene} at matrix line {i}")

    data = {}
    for signature in SIGNATURES:
        if counts[signature] > 0:
            data[signature] = accum[signature] / counts[signature]
        else:
            data[signature] = np.full(n_cells, np.nan, dtype=np.float32)
    return pd.DataFrame(data), found


def save_plots(sample_scores: pd.DataFrame) -> None:
    plot_specs = [
        (
            "T lymphocytes",
            ["T_CELL_EXHAUSTION", "CYTOTOXICITY"],
            "tcell_signature_scores_by_site.png",
            "T-cell signatures",
        ),
        (
            "Myeloid cells",
            ["MYELOID_INFLAMMATION", "MACROPHAGE_LIKE"],
            "myeloid_signature_scores_by_site.png",
            "Myeloid signatures",
        ),
        (
            "Epithelial cells",
            ["EMT_INVASION", "HYPOXIA", "PROLIFERATION"],
            "epithelial_signature_scores_by_site.png",
            "Epithelial/tumor-associated signatures",
        ),
    ]

    for cell_type, signatures, filename, title in plot_specs:
        subset = sample_scores[sample_scores["cell_type_clean"] == cell_type].copy()
        if subset.empty:
            continue
        long_df = subset.melt(
            id_vars=["sample", "tissue_site", "cell_type_clean", "n_cells"],
            value_vars=signatures,
            var_name="signature",
            value_name="score",
        )
        plt.figure(figsize=(10, 5))
        sns.boxplot(data=long_df, x="tissue_site", y="score", hue="signature", showfliers=False)
        sns.stripplot(data=long_df, x="tissue_site", y="score", hue="signature", dodge=True, color="black", alpha=0.5, size=2)
        plt.xticks(rotation=35, ha="right")
        plt.title(title)
        plt.xlabel("")
        plt.ylabel("Mean log-normalized signature score")
        handles, labels = plt.gca().get_legend_handles_labels()
        n = len(signatures)
        plt.legend(handles[:n], labels[:n], title="Signature", bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.tight_layout()
        for path in [RESULTS_FIGURES / filename, DOCS_FIGURES / filename]:
            plt.savefig(path, dpi=300)
        plt.close()

    heatmap = (
        sample_scores.groupby(["tissue_site", "cell_type_clean"], observed=True)[list(SIGNATURES)]
        .mean()
        .reset_index()
    )
    heatmap["site_celltype"] = heatmap["tissue_site"] + " | " + heatmap["cell_type_clean"]
    matrix = heatmap.set_index("site_celltype")[list(SIGNATURES)]
    matrix = matrix.dropna(how="all")
    plt.figure(figsize=(9, max(5, 0.28 * matrix.shape[0])))
    sns.heatmap(matrix, cmap="viridis", linewidths=0.2)
    plt.xlabel("")
    plt.ylabel("")
    plt.title("Mean TME signature scores by tissue site and cell type")
    plt.tight_layout()
    for path in [RESULTS_FIGURES / "tme_signature_heatmap_by_site_celltype.png", DOCS_FIGURES / "tme_signature_heatmap_by_site_celltype.png"]:
        plt.savefig(path, dpi=300)
    plt.close()


def main() -> None:
    ensure_dirs()
    config = load_config()
    matrix_path = DATA_RAW / config["files"]["raw_umi_txt"]
    metadata_path = DATA_METADATA / "gse131907_cell_metadata_clean.csv"
    if not matrix_path.exists():
        raise FileNotFoundError(f"Missing {matrix_path}. Run scripts/00_download_geo.py --raw-only first.")
    if not metadata_path.exists():
        raise FileNotFoundError("Run scripts/01_metadata_overview.py first.")

    meta = pd.read_csv(metadata_path, dtype=str)
    cells = read_header(matrix_path)
    print(f"Raw UMI matrix contains {len(cells)} cells.")
    order = pd.DataFrame({"Index": cells, "matrix_order": np.arange(len(cells))})
    meta_ordered = order.merge(meta, on="Index", how="left")
    if meta_ordered["sample"].isna().any():
        missing = meta_ordered["sample"].isna().sum()
        raise ValueError(f"{missing} matrix cells could not be matched to metadata by Index.")

    library = compute_library_sizes(matrix_path, len(cells))
    pd.DataFrame({"Index": cells, "library_size": library}).to_csv(RESULTS_TABLES / "cell_library_sizes.csv", index=False)
    scores, found = score_signatures(matrix_path, library)
    cell_scores = pd.concat([meta_ordered.drop(columns=["matrix_order"]), scores], axis=1)
    cell_scores.to_csv(RESULTS_TABLES / "cell_signature_scores_selected_genes.csv", index=False)

    score_cols = list(SIGNATURES)
    sample_scores = (
        cell_scores.groupby(["sample", "patient_id", "tissue_site", "cell_type_clean"], observed=True)
        .agg(n_cells=("Index", "size"), **{col: (col, "mean") for col in score_cols})
        .reset_index()
    )
    sample_scores.to_csv(RESULTS_TABLES / "signature_scores_by_sample_celltype.csv", index=False)
    sample_scores.to_csv(DOCS_TABLES / "signature_scores_by_sample_celltype.csv", index=False)

    tissue_scores = (
        sample_scores.groupby(["tissue_site", "cell_type_clean"], observed=True)[["n_cells"] + score_cols]
        .mean(numeric_only=True)
        .reset_index()
    )
    tissue_scores.to_csv(RESULTS_TABLES / "signature_scores_by_tissue_celltype.csv", index=False)
    tissue_scores.to_csv(DOCS_TABLES / "signature_scores_by_tissue_celltype.csv", index=False)

    found_df = pd.DataFrame(
        [{"signature": signature, "n_genes_found": len(genes), "genes_found": ";".join(genes)} for signature, genes in found.items()]
    )
    found_df.to_csv(RESULTS_TABLES / "signature_genes_found.csv", index=False)
    found_df.to_csv(DOCS_TABLES / "signature_genes_found.csv", index=False)

    save_plots(sample_scores)
    print("Wrote expression-based TME signature scores and figures.")


if __name__ == "__main__":
    main()
