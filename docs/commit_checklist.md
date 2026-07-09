# Commit Checklist

Use this checklist before committing the upgraded LUAD reanalysis repo.

## Quick Review

- Read `README.md` for the public-facing overview.
- Read `docs/project_brief.md` for the short portfolio-style summary.
- Read `docs/results_summary.md` for the current interpretation.
- Read `docs/output_guide.md` for the file-by-file output map.
- Confirm the new figures render on GitHub after pushing.

## Local Checks

Run:

```bash
python3 scripts/08_validate_outputs.py
PYTHONPYCACHEPREFIX=/tmp/gse131907_pycache python3 -m py_compile scripts/*.py
python3 -m json.tool notebooks/01_dataset_overview.ipynb >/tmp/gse131907_notebook_check.json
```

The validation script checks committed figures, tables, required documentation, notebook structure, Quarto report links, and local Markdown links.

Optional full workflow rerun, if the raw GEO matrix is still present locally:

```bash
MPLCONFIGDIR=/tmp/gse131907_mpl PYTHONPYCACHEPREFIX=/tmp/gse131907_pycache bash scripts/run_all.sh --with-expression
```

## Suggested Commit

```bash
git add .github CHANGELOG.md CITATION.cff README.md data docs environment.yml notebooks reports requirements.txt results scripts workflow
git commit -m "Add subtype and paired-patient LUAD TME analyses"
git push
```

## After Push

- Check the GitHub Actions workflow completes successfully.
- Open the README on GitHub and confirm all embedded figures display.
- Use `docs/github_repo_setup.md` to update the repository description and topics.
- Confirm large raw files remain untracked.
