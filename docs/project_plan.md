# Project Plan

## Current Deliverable

- download GEO cell annotation file
- infer sample and tissue-site metadata
- summarize cells per sample and site
- summarize cell-type composition per sample and site
- stream the raw UMI matrix for selected tumor microenvironment signature scoring
- summarize signatures by sample, tissue site, broad cell type, and annotated subtype
- run sample-level tissue-site contrasts with effect sizes and FDR correction
- run paired-patient sensitivity checks where matched tissue contexts exist
- generate GitHub preview figures/tables and a lightweight companion notebook

## Independent Analysis Direction

Rather than reproducing the original LUAD atlas, this project focuses on sample-aware tumor microenvironment differences across tissue contexts.

Completed first-pass extensions:

- curated mean-gene scoring for immune exhaustion, cytotoxicity, myeloid inflammation, macrophage-like activity, EMT/invasion, hypoxia, and proliferation
- subtype-level summaries using the GEO `Cell_subtype` labels
- paired-patient sensitivity checks for selected matched tissue contrasts

Possible future extensions:

- benchmark cell-type annotation tools against the provided annotations
- compare mean-gene scoring against AUCell, decoupler, or GSVA-style activity scoring
- test sample-level composition methods such as simple proportions vs scCODA/Milo-style approaches
- perform subtype-level pseudo-bulk DE using raw UMI counts where feasible
- evaluate malignant epithelial programs with copy-number-aware malignant-cell filtering
