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

## Contrast Testing

`scripts/05_signature_statistics.py` compares selected signature scores between tissue sites within relevant cell compartments. Current contrasts include:

- T lymphocytes: tumor-associated sites versus normal lymph node for exhaustion and cytotoxicity
- Myeloid cells: tumor-associated sites versus normal lymph node for inflammatory and macrophage-like programs
- Epithelial cells: tumor-associated sites versus normal lung for EMT/invasion, hypoxia, and proliferation

For each contrast, the script reports:

- number of contributing sample/cell-type profiles
- mean score in the contrast and reference groups
- mean difference
- Cohen's d
- Mann-Whitney U p-value
- Benjamini-Hochberg adjusted p-value

Recommended next steps:

- extend the current paired-patient sensitivity checks into formal mixed-effect modeling where sample sizes support it
- subset malignant epithelial cells before interpreting EMT/hypoxia/proliferation biologically
- compare simple mean-gene scoring against AUCell, decoupler, or GSVA-style methods
- evaluate whether results are robust to minimum cell-count thresholds per sample/cell type

## Paired-Patient Sensitivity Checks

`scripts/07_paired_patient_analysis.py` uses `signature_scores_by_sample_celltype.csv` to compare tissue contexts within the same patient where matched samples are available.

The script reports:

- number of paired patients
- mean and median within-patient score difference
- Wilcoxon signed-rank p-value
- Benjamini-Hochberg adjusted p-value
- contributing paired patient IDs

These checks are most informative for contrasts with larger paired counts, such as primary tumor versus normal lung epithelial signatures. Comparisons with only a few paired patients are retained for transparency but should be treated as descriptive.
