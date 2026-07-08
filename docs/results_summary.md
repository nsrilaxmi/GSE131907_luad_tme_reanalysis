# Results Summary

This summary describes the current first-pass outputs from the sample-aware `GSE131907` LUAD tumor microenvironment reanalysis.

A compact machine-readable list of headline findings is available in `docs/tables/key_results_summary.csv`.

## Dataset Recovery

- The GEO cell annotation file contains 208,506 annotated cells.
- The workflow recovers 58 named samples across:
  - advanced airway tumor
  - primary tumor
  - pleural effusion
  - normal lung
  - non-smoker lung
  - normal lymph node
- Broad cell labels include T lymphocytes, myeloid cells, epithelial cells, B lymphocytes, NK cells, fibroblasts, mast cells, endothelial cells, oligodendrocytes, and undetermined cells.

## Composition Patterns

- Normal lymph node samples are dominated by lymphocytes, as expected.
- Lung and tumor sites contain mixed epithelial, myeloid, T-cell, B-cell, and stromal compartments.
- Pleural effusion samples show prominent T-cell and immune compartments with comparatively fewer epithelial cells.

## Expression-Based Signature Patterns

The upgraded workflow streams the raw UMI matrix and scores curated tumor microenvironment signatures after library-size normalization.

First-pass patterns:

- T lymphocytes show higher exhaustion scores in tumor-associated contexts than in normal lymph node.
- Cytotoxicity is highest in normal lung T lymphocytes and remains evident in tumor-associated sites.
- Myeloid inflammation is elevated in advanced airway tumor, pleural effusion, normal/non-smoker lung, and primary tumor relative to normal lymph node.
- Macrophage-like signatures are strongest in lung and primary tumor myeloid compartments.
- Epithelial hypoxia and proliferation scores are higher in advanced airway tumor and pleural effusion epithelial cells than in normal lung epithelial cells.

## Sample-Level Signature Contrasts

`scripts/05_signature_statistics.py` adds a focused sample-level testing layer for selected cell-type/signature pairs.

Strongest first-pass contrasts include:

- higher epithelial hypoxia in advanced airway tumor than normal lung
- higher epithelial proliferation in advanced airway tumor and pleural effusion than normal lung
- higher myeloid inflammation in primary tumor, advanced airway tumor, and pleural effusion than normal lymph node
- higher macrophage-like scores in primary tumor and advanced airway tumor than normal lymph node
- higher T-cell cytotoxicity in primary tumor and advanced airway tumor than normal lymph node
- higher T-cell exhaustion in primary tumor and advanced airway tumor than normal lymph node

These tests are still exploratory: they use sample/cell-type-level summaries, but tissue-site groups are observational and vary in sample number and composition.

## Paired-Patient Sensitivity Checks

Some patients contribute more than one tissue context, allowing a limited within-patient check of selected contrasts.

`scripts/07_paired_patient_analysis.py` summarizes these paired differences for relevant cell-type/signature pairs. This is not a replacement for a formal mixed model, but it helps flag whether the largest tissue-site patterns are supported by patients with matched reference and contrast samples.

The paired results should be interpreted cautiously because the number of paired patients varies by comparison.

## Cell-Subtype Patterns

`scripts/06_subtype_analysis.py` adds a focused subtype layer using the GEO `Cell_subtype` annotations.

First-pass subtype outputs show:

- abundant malignant cells, naive CD4 T cells, follicular B cells, monocyte-derived macrophages, and alveolar macrophages across the atlas
- T-cell subtype summaries that separate naive, cytotoxic, exhausted, regulatory, and helper-like T-cell states
- myeloid subtype summaries that distinguish alveolar macrophages, monocyte-derived macrophages, monocytes, pleural macrophages, and dendritic-cell groups
- epithelial subtype summaries that keep malignant-cell and normal epithelial subtype patterns visible instead of collapsing everything into one broad epithelial label

The subtype analysis is still descriptive, but it makes the repo scientifically stronger because it connects broad TME programs to more interpretable annotated populations.

## Current Strengths

- Uses sample/tissue-site-aware summaries instead of only cell-level plots.
- Keeps large GEO files out of Git while providing reproducible download scripts.
- Adds expression-based TME signature scoring without loading the full expression matrix into memory.
- Adds sample-level signature contrasts with effect sizes and FDR correction.
- Adds paired-patient sensitivity checks for tissue contrasts where matched patients are available.
- Adds subtype-aware composition and signature summaries from the original cell annotations.
- Provides compact preview figures and tables suitable for GitHub review.

## Recommended Next Analysis

- Compare signature scoring methods, such as mean-gene scoring versus AUCell/decoupler-style activity scoring.
- Extend the paired-patient checks into a formal mixed-effect model where sample sizes support it.
- Subset epithelial cells and evaluate malignant-like programs more carefully before making tumor-cell-specific claims.
