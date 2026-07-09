# Output Guide

This guide summarizes the committed preview outputs in `docs/figures/` and `docs/tables/`. The large GEO inputs and full intermediate files are intentionally kept out of Git.

## Start Here

Recommended review order:

1. `docs/results_summary.md` for the interpretation.
2. `docs/tables/key_results_summary.csv` for a compact table of headline findings.
3. `docs/figures/signature_contrast_effect_sizes.png` for sample-level tissue-site differences.
4. `docs/figures/paired_patient_signature_deltas.png` for within-patient sensitivity checks.
5. `docs/figures/signature_score_sensitivity.png` for score-scaling robustness.
6. `docs/figures/top_subtypes_by_tissue.png` and subtype heatmaps for cell-state context.
7. `notebooks/01_dataset_overview.ipynb` for interactive table inspection.

## Main Figures

| Figure | Purpose |
| --- | --- |
| `sample_counts_by_tissue.png` | Shows per-sample cell recovery and tissue-site labels. |
| `celltype_composition_by_sample.png` | Shows broad cell-type composition for each sample. |
| `top_celltypes_by_site.png` | Summarizes broad cell-type composition by tissue site. |
| `tcell_signature_scores_by_site.png` | Compares T-cell exhaustion and cytotoxicity signatures across sites. |
| `myeloid_signature_scores_by_site.png` | Compares myeloid inflammation and macrophage-like signatures across sites. |
| `epithelial_signature_scores_by_site.png` | Compares EMT/invasion, hypoxia, and proliferation signatures in epithelial cells. |
| `tme_signature_heatmap_by_site_celltype.png` | Provides an overview of mean signature activity by site and broad cell type. |
| `signature_contrast_effect_sizes.png` | Displays the largest sample-level mean signature differences. |
| `paired_patient_signature_deltas.png` | Displays within-patient differences where matched tissue contexts exist. |
| `signature_score_sensitivity.png` | Compares contrast directions under original and standardized signature scoring summaries. |
| `top_subtypes_by_tissue.png` | Shows abundant annotated cell subtypes by tissue site. |
| `tcell_subtype_signature_heatmap.png` | Shows T-cell subtype-level exhaustion and cytotoxicity patterns. |
| `myeloid_subtype_signature_heatmap.png` | Shows myeloid subtype-level inflammatory and macrophage-like patterns. |
| `epithelial_subtype_signature_heatmap.png` | Shows epithelial subtype-level EMT/invasion, hypoxia, and proliferation patterns. |

## Main Tables

| Table | Purpose |
| --- | --- |
| `cell_counts_by_sample.csv` | Cell counts per sample and tissue site. |
| `celltype_composition_by_sample.csv` | Broad cell-type counts and fractions per sample. |
| `tissue_site_summary.csv` | Broad cell-type counts and fractions per tissue site. |
| `planned_tme_signatures.csv` | Curated gene sets used for first-pass TME scoring. |
| `signature_genes_found.csv` | Confirms which signature genes were found in the raw UMI matrix. |
| `signature_scores_by_sample_celltype.csv` | Signature scores summarized by sample and broad cell type. |
| `signature_scores_by_tissue_celltype.csv` | Signature scores summarized by tissue site and broad cell type. |
| `key_results_summary.csv` | Compact table of selected headline findings from sample-level and paired-patient contrasts. |
| `signature_contrast_sensitivity.csv` | Checks whether contrast directions agree after z-score and rank-percentile score scaling. |
| `signature_score_method_correlations.csv` | Summarizes correlations between original mean scores and scaled score summaries. |
| `signature_site_contrasts.csv` | Sample-level Mann-Whitney contrasts with effect sizes and FDR correction. |
| `paired_patient_signature_contrasts.csv` | Within-patient contrast summaries and paired patient IDs. |
| `subtype_composition_by_sample.csv` | Cell subtype counts and fractions per sample. |
| `subtype_composition_by_tissue.csv` | Cell subtype counts and fractions per tissue site. |
| `signature_scores_by_sample_subtype.csv` | Signature scores summarized by sample and cell subtype. |
| `signature_scores_by_tissue_subtype.csv` | Signature scores summarized by tissue site and cell subtype. |

## Interpretation Notes

- The strongest paired-patient signal is higher epithelial hypoxia in primary tumor compared with normal lung.
- Headline contrast directions are stable after z-score and rank-percentile scaling of sample-level signature scores.
- Immune paired-patient contrasts are useful but smaller; many have only three paired patients.
- Signature scores are compact exploratory summaries and should not be interpreted as formal differential expression.
- Cell subtype labels come from the public GEO annotation and are used here for focused reanalysis, not independent annotation discovery.

## Validation

Run:

```bash
python3 scripts/08_validate_outputs.py
```

This checks that committed figures, tables, required documentation, notebook structure, report links, and local Markdown links are present and internally consistent.
