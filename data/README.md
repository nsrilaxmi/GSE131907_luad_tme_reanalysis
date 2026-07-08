# Data Directory

Large GEO files are downloaded locally into `data/raw_geo/` and are intentionally ignored by Git.

## Download Options

For the lightweight metadata/composition workflow:

```bash
python3 scripts/00_download_geo.py --annotation-only
```

For the expression-driven signature workflow:

```bash
python3 scripts/00_download_geo.py --raw-only
```

The raw UMI matrix is large and is used by `scripts/04_signature_scoring.py` through a streaming two-pass parser. The normalized log2TPM matrix is not required for the current workflow.

## Generated Metadata

`scripts/01_metadata_overview.py` writes cleaned sample and cell metadata into `data/metadata/` and `results/tables/`. Metadata CSV files are ignored by Git because they are reproducible from the GEO annotation supplement.

## Git Policy

This repository commits small preview outputs in `docs/`, but does not commit raw GEO files or large local intermediates.
