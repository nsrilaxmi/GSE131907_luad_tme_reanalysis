# Snakemake Workflow

This folder provides an optional Snakemake entry point for the LUAD TME reanalysis.

The script-based workflow remains supported:

```bash
bash scripts/run_all.sh --with-expression
```

## Install Snakemake

Using conda or mamba:

```bash
conda install -c conda-forge -c bioconda snakemake
```

## Run Lightweight Metadata/Composition Workflow

From the repository root:

```bash
snakemake --snakefile workflow/Snakefile --cores 4
```

This target downloads the GEO annotation file if needed, builds cleaned metadata, and regenerates the composition preview outputs.

## Run Full Expression Workflow

From the repository root:

```bash
snakemake --snakefile workflow/Snakefile --cores 4 full
```

This target also downloads the raw UMI matrix if needed and regenerates expression-based TME signatures, sample-level contrasts, subtype summaries, paired-patient checks, score-sensitivity summaries, and the key-results table.

## Dry Run

```bash
snakemake --snakefile workflow/Snakefile --cores 1 --dry-run
```

The Snakemake workflow documents dependencies between the existing scripts. It does not replace the Python scripts; it makes the execution graph explicit for reproducibility and GitHub review.
