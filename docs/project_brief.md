# Project Brief

## Title

Sample-aware reanalysis of the lung adenocarcinoma tumor microenvironment single-cell atlas `GSE131907`

## One-Sentence Summary

This project reanalyzes public lung adenocarcinoma single-cell RNA-seq data with a sample-aware workflow focused on tumor microenvironment composition, curated immune/myeloid/epithelial signatures, cell-subtype context, and paired-patient sensitivity checks.

## Dataset

`GSE131907` contains 208,506 annotated single cells from 58 lung adenocarcinoma-related samples across normal lung, primary tumor, normal lymph node, advanced airway tumor samples, non-smoker lung, and pleural effusion.

This reanalysis uses the public GEO annotation and raw UMI matrix supplements. Large GEO files are downloaded locally and are not committed to GitHub.

## Analysis Angle

The original study is a detailed lung adenocarcinoma atlas. This repository does not try to reproduce every original analysis. Instead, it asks a compact portfolio-style question:

How do tumor microenvironment composition and selected expression programs vary across tissue contexts when results are summarized at the sample, tissue-site, broad-cell-type, and annotated-cell-subtype levels?

## Methods Snapshot

- Standardized sample, tissue-site, patient, broad cell-type, and subtype metadata from the GEO annotation file.
- Summarized broad cell-type and cell-subtype composition by sample and tissue site.
- Streamed the raw UMI matrix in two passes to avoid loading the full matrix into memory.
- Scored curated TME signatures after library-size normalization using mean log-normalized expression.
- Tested selected sample-level tissue-site contrasts with Mann-Whitney U tests, Cohen's d, and Benjamini-Hochberg FDR correction.
- Added paired-patient sensitivity checks where the same patient had both reference and contrast tissue contexts.
- Added a score-scaling sensitivity check comparing original mean scores with z-score and rank-percentile summaries.
- Generated compact GitHub-preview figures, tables, a companion notebook, and validation checks.

## Key First-Pass Findings

See `docs/tables/key_results_summary.csv` for a compact machine-readable summary of these headline findings.

- Epithelial hypoxia is higher in advanced airway tumor epithelial cells than normal lung epithelial cells in the sample-level contrast table.
- Primary tumor epithelial hypoxia is also higher than matched normal lung in the paired-patient sensitivity check with 10 paired patients.
- Myeloid inflammation and macrophage-like signatures are higher in tumor-associated sites than normal lymph node in sample-level contrasts.
- T-cell cytotoxicity and exhaustion programs are elevated in several tumor-associated contexts relative to normal lymph node.
- Headline contrast directions remain stable after z-score and rank-percentile score scaling.
- Subtype summaries show that broad immune and epithelial signals can be linked back to more interpretable annotated populations, including macrophage, T-cell, malignant epithelial, AT1/AT2, and tumor-state epithelial labels.

## Strongest Result to Mention

The most defensible single result is the paired-patient epithelial hypoxia signal: primary tumor epithelial cells show higher hypoxia signature scores than matched normal lung epithelial cells across 10 paired patients.

This is still exploratory, but it is stronger than a purely between-patient comparison because the contrast is evaluated within patients where matched tissue contexts are available.

## Why This Repo Is Different From a Notebook Dump

- It separates data download, metadata processing, composition summaries, signature scoring, statistical contrasts, subtype analysis, paired-patient checks, and validation into scripts.
- It commits small preview outputs while keeping large GEO and intermediate files out of Git.
- It includes a README, output guide, results summary, report scaffold, notebook, citation metadata, license, and GitHub Actions checks.
- It makes assumptions and limitations explicit, especially around observational tissue-site comparisons and inherited public annotations.

## Limitations

- The analysis starts from public processed supplements and annotations.
- Tissue-site comparisons are observational and not causal.
- Some paired-patient contrasts have small paired sample counts.
- Signature scores are exploratory summaries, not full differential expression or pathway activity models.
- Malignant-cell-specific claims should be strengthened with copy-number-aware malignant-cell filtering in future work.

## Reuse Statement

This repository is best viewed as a reproducible public-data reanalysis workflow and portfolio project. It can support future extensions such as method benchmarking, mixed-effect modeling, malignant-cell-focused analysis, or comparison of gene-set scoring methods.
