# Results Directory

Generated figures and tables are written here when the workflow is run locally.

The workflow also writes GitHub-preview versions of selected outputs directly into:

```text
docs/figures/
docs/tables/
```

Files in `results/` are ignored by Git because they are reproducible local intermediates. The committed `docs/` outputs are intentionally small enough for GitHub review.

To regenerate the full local result set:

```bash
python3 scripts/00_download_geo.py --annotation-only
python3 scripts/00_download_geo.py --raw-only
bash scripts/run_all.sh --with-expression
```

To validate committed preview outputs:

```bash
python3 scripts/08_validate_outputs.py
```
