# Results Summary

This summary describes the current first-pass outputs from the sample-aware `GSE131907` LUAD tumor microenvironment reanalysis.

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

These findings are exploratory and should be followed by sample-aware statistical testing and more refined cell-state analysis.

## Current Strengths

- Uses sample/tissue-site-aware summaries instead of only cell-level plots.
- Keeps large GEO files out of Git while providing reproducible download scripts.
- Adds expression-based TME signature scoring without loading the full expression matrix into memory.
- Provides compact preview figures and tables suitable for GitHub review.

## Recommended Next Analysis

- Add minimum cell-count filtering before plotting sample-level signature scores.
- Compare signature scoring methods, such as mean-gene scoring versus AUCell/decoupler-style activity scoring.
- Perform cell-subtype-specific summaries using `Cell_subtype` in the GEO annotation.
- Add sample-aware statistical tests for selected signatures.
- Subset epithelial cells and evaluate malignant-like programs more carefully before making tumor-cell-specific claims.

