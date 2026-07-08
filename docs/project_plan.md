# Project Plan

## First-Pass Deliverable

- download GEO cell annotation file
- infer sample and tissue-site metadata
- summarize cells per sample and site
- summarize cell-type composition per sample and site
- generate GitHub preview figures/tables

## Independent Analysis Direction

Rather than reproducing the original LUAD atlas, this project focuses on sample-aware tumor microenvironment differences across tissue contexts.

Possible extensions:

- benchmark cell-type annotation tools against the provided annotations
- compare gene-set scoring methods for immune exhaustion, cytotoxicity, EMT, hypoxia, and proliferation
- test sample-level composition methods such as simple proportions vs scCODA/Milo-style approaches
- perform subtype-level pseudo-bulk DE using raw UMI counts where feasible

