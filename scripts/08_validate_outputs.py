from __future__ import annotations

import csv
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_FIGURES = PROJECT_ROOT / "docs" / "figures"
DOCS_TABLES = PROJECT_ROOT / "docs" / "tables"


REQUIRED_FIGURES = [
    "sample_counts_by_tissue.png",
    "celltype_composition_by_sample.png",
    "top_celltypes_by_site.png",
    "tcell_signature_scores_by_site.png",
    "myeloid_signature_scores_by_site.png",
    "epithelial_signature_scores_by_site.png",
    "tme_signature_heatmap_by_site_celltype.png",
    "signature_contrast_effect_sizes.png",
    "paired_patient_signature_deltas.png",
    "top_subtypes_by_tissue.png",
    "tcell_subtype_signature_heatmap.png",
    "myeloid_subtype_signature_heatmap.png",
    "epithelial_subtype_signature_heatmap.png",
]


REQUIRED_TABLE_COLUMNS = {
    "cell_counts_by_sample.csv": {"sample", "patient_id", "tissue_site", "n_cells"},
    "celltype_composition_by_sample.csv": {"sample", "patient_id", "tissue_site", "cell_type_clean", "n_cells", "fraction"},
    "tissue_site_summary.csv": {"tissue_site", "cell_type_clean", "n_cells", "fraction"},
    "signature_genes_found.csv": {"signature", "n_genes_found", "genes_found"},
    "signature_scores_by_sample_celltype.csv": {"sample", "patient_id", "tissue_site", "cell_type_clean", "n_cells"},
    "signature_scores_by_tissue_celltype.csv": {"tissue_site", "cell_type_clean", "n_cells"},
    "key_results_summary.csv": {"result_type", "cell_type", "signature", "comparison", "n", "effect", "effect_label", "padj_bh", "interpretation"},
    "signature_site_contrasts.csv": {"cell_type_clean", "signature", "contrast", "delta_mean", "pvalue", "padj_bh"},
    "paired_patient_signature_contrasts.csv": {"cell_type_clean", "signature", "contrast", "n_paired_patients", "mean_paired_delta", "padj_bh"},
    "subtype_composition_by_sample.csv": {"sample", "patient_id", "tissue_site", "cell_type_clean", "Cell_subtype", "n_cells"},
    "subtype_composition_by_tissue.csv": {"tissue_site", "cell_type_clean", "Cell_subtype", "n_cells", "fraction"},
    "signature_scores_by_sample_subtype.csv": {"sample", "patient_id", "tissue_site", "cell_type_clean", "Cell_subtype", "n_cells"},
    "signature_scores_by_tissue_subtype.csv": {"tissue_site", "cell_type_clean", "Cell_subtype", "total_cells", "n_sample_subtypes"},
}


EXPECTED_SIGNATURES = {
    "T_CELL_EXHAUSTION",
    "CYTOTOXICITY",
    "MYELOID_INFLAMMATION",
    "MACROPHAGE_LIKE",
    "EMT_INVASION",
    "HYPOXIA",
    "PROLIFERATION",
}


REQUIRED_DOCS = [
    "commit_checklist.md",
    "data_availability.md",
    "github_repo_setup.md",
    "methods_overview.md",
    "output_guide.md",
    "project_brief.md",
    "project_plan.md",
    "results_summary.md",
    "signature_scoring_notes.md",
]


REQUIRED_REPOSITORY_FILES = [
    "CITATION.cff",
    "CHANGELOG.md",
    "LICENSE",
    "README.md",
    "config.yaml",
    "data/README.md",
    "results/README.md",
]


MARKDOWN_FILES_FOR_LINK_CHECK = [
    "README.md",
    "CHANGELOG.md",
    "data/README.md",
    "results/README.md",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def read_csv_header(path: Path) -> list[str]:
    with path.open(newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def count_csv_rows(path: Path) -> int:
    with path.open(newline="") as handle:
        return max(0, sum(1 for _ in handle) - 1)


def validate_figures() -> None:
    for filename in REQUIRED_FIGURES:
        path = DOCS_FIGURES / filename
        if not path.exists():
            fail(f"Missing figure: {path.relative_to(PROJECT_ROOT)}")
        if path.stat().st_size < 1024:
            fail(f"Figure appears too small or empty: {path.relative_to(PROJECT_ROOT)}")


def validate_tables() -> None:
    for filename, required_columns in REQUIRED_TABLE_COLUMNS.items():
        path = DOCS_TABLES / filename
        if not path.exists():
            fail(f"Missing table: {path.relative_to(PROJECT_ROOT)}")
        header = set(read_csv_header(path))
        missing = required_columns - header
        if missing:
            fail(f"{filename} is missing columns: {sorted(missing)}")
        if count_csv_rows(path) == 0:
            fail(f"{filename} has no data rows.")

    signature_path = DOCS_TABLES / "signature_genes_found.csv"
    with signature_path.open(newline="") as handle:
        found = {row["signature"] for row in csv.DictReader(handle)}
    missing_signatures = EXPECTED_SIGNATURES - found
    if missing_signatures:
        fail(f"signature_genes_found.csv is missing signatures: {sorted(missing_signatures)}")


def validate_notebook() -> None:
    notebook_path = PROJECT_ROOT / "notebooks" / "01_dataset_overview.ipynb"
    with notebook_path.open() as handle:
        notebook = json.load(handle)
    if notebook.get("nbformat") != 4:
        fail("Notebook is not nbformat 4.")
    if len(notebook.get("cells", [])) < 5:
        fail("Notebook has fewer cells than expected.")


def validate_docs() -> None:
    for filename in REQUIRED_REPOSITORY_FILES:
        path = PROJECT_ROOT / filename
        if not path.exists():
            fail(f"Missing repository file: {filename}")
        if path.stat().st_size < 100:
            fail(f"Repository file appears too small: {filename}")

    for filename in REQUIRED_DOCS:
        path = PROJECT_ROOT / "docs" / filename
        if not path.exists():
            fail(f"Missing documentation file: docs/{filename}")
        if path.stat().st_size < 200:
            fail(f"Documentation file appears too small: docs/{filename}")


def validate_report_links() -> None:
    report_path = PROJECT_ROOT / "reports" / "08_final_report.qmd"
    text = report_path.read_text()
    figures = re.findall(r'show_png\("([^"]+)"', text)
    tables = re.findall(r'docs / "tables" / "([^"]+)"', text)
    for filename in figures:
        if not (DOCS_FIGURES / filename).exists():
            fail(f"Report references missing figure: {filename}")
    for filename in tables:
        if not (DOCS_TABLES / filename).exists():
            fail(f"Report references missing table: {filename}")


def is_external_or_anchor(target: str) -> bool:
    return (
        target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("mailto:")
        or target.startswith("#")
        or target.startswith("data:")
    )


def validate_markdown_links() -> None:
    files = [PROJECT_ROOT / path for path in MARKDOWN_FILES_FOR_LINK_CHECK]
    files.extend((PROJECT_ROOT / "docs").glob("*.md"))
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for markdown_path in files:
        text = markdown_path.read_text()
        for raw_target in link_pattern.findall(text):
            target = raw_target.split()[0].strip("<>")
            if is_external_or_anchor(target):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = (markdown_path.parent / target).resolve()
            try:
                resolved.relative_to(PROJECT_ROOT)
            except ValueError:
                fail(f"{markdown_path.relative_to(PROJECT_ROOT)} links outside the repository: {raw_target}")
            if not resolved.exists():
                fail(f"{markdown_path.relative_to(PROJECT_ROOT)} has broken local link: {raw_target}")


def main() -> None:
    validate_figures()
    validate_tables()
    validate_notebook()
    validate_docs()
    validate_report_links()
    validate_markdown_links()
    print("Validated committed figures, tables, docs, notebook, and report/Markdown links.")


if __name__ == "__main__":
    main()
