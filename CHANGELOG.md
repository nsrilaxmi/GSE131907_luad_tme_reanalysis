# Changelog

## 2026-07-08

Major repository upgrade for the `GSE131907` LUAD tumor microenvironment reanalysis.

### Added

- Expression-based TME signature scoring from the raw UMI matrix.
- Sample-level tissue-site contrast testing with effect sizes and FDR correction.
- Cell-subtype composition and signature summaries using GEO `Cell_subtype` labels.
- Paired-patient sensitivity checks where matched tissue contexts exist.
- Signature score-scaling sensitivity checks for headline contrast robustness.
- New committed preview figures and tables under `docs/`.
- Project brief, output guide, updated results summary, and expanded report scaffold.
- Lightweight validation script for committed outputs, documentation, notebook structure, and report links.
- GitHub Actions validation for Python syntax and committed output integrity.
- Optional Snakemake workflow entry point under `workflow/`.

### Improved

- README now explains the biological question, independent reanalysis angle, full workflow, and key outputs.
- Companion notebook now inspects generated composition, signature, subtype, and paired-patient outputs.
- Data/results directory notes now clarify what is reproducible locally and what is committed for GitHub preview.
- Citation metadata now includes a clearer abstract, release date, and MIT license metadata.

### Validation

Local checks passing:

```bash
python3 scripts/08_validate_outputs.py
python3 -m py_compile scripts/*.py
python3 -m json.tool notebooks/01_dataset_overview.ipynb
```
