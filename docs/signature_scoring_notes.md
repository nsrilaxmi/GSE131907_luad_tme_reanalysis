# Signature Scoring Notes

The expression-driven workflow scores selected tumor microenvironment signatures from the raw UMI matrix without loading the full matrix into memory.

## Input

```text
data/raw_geo/GSE131907_Lung_Cancer_raw_UMI_matrix.txt.gz
```

The matrix is gene-by-cell, with the first column containing gene symbols and the remaining columns containing cell identifiers.

## Method

`scripts/04_signature_scoring.py` uses two streaming passes:

1. Compute total UMI library size for every cell across all genes.
2. Re-scan the matrix and extract only the genes used in curated TME signatures.

Each captured gene is transformed as:

```text
log1p(raw_count / cell_library_size * 10000)
```

Signature scores are the mean of available transformed genes per signature.

## Signatures

- `T_CELL_EXHAUSTION`
- `CYTOTOXICITY`
- `MYELOID_INFLAMMATION`
- `MACROPHAGE_LIKE`
- `EMT_INVASION`
- `HYPOXIA`
- `PROLIFERATION`

All planned genes were found in the raw UMI matrix in the current run. See:

```text
docs/tables/signature_genes_found.csv
```

## Interpretation

These scores are exploratory summaries, not formal differential expression tests. They are intended to show tissue-site and compartment-level TME patterns while respecting sample and cell-type structure.

Recommended next steps:

- add sample-aware statistical testing for selected signatures
- subset malignant epithelial cells before interpreting EMT/hypoxia/proliferation biologically
- compare simple mean-gene scoring against AUCell, decoupler, or GSVA-style methods
- evaluate whether results are robust to minimum cell-count thresholds per sample/cell type

