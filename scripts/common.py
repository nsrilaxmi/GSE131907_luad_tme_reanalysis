from __future__ import annotations

from pathlib import Path
from typing import Iterable
import re

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw_geo"
DATA_METADATA = PROJECT_ROOT / "data" / "metadata"
RESULTS_FIGURES = PROJECT_ROOT / "results" / "figures"
RESULTS_TABLES = PROJECT_ROOT / "results" / "tables"
DOCS_FIGURES = PROJECT_ROOT / "docs" / "figures"
DOCS_TABLES = PROJECT_ROOT / "docs" / "tables"


def ensure_dirs() -> None:
    for path in [DATA_RAW, DATA_METADATA, RESULTS_FIGURES, RESULTS_TABLES, DOCS_FIGURES, DOCS_TABLES]:
        path.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    with (PROJECT_ROOT / "config.yaml").open() as handle:
        return yaml.safe_load(handle)


def first_existing_column(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    lower_lookup = {col.lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        if candidate.lower() in lower_lookup:
            return lower_lookup[candidate.lower()]
    return None


def infer_sample_column(meta: pd.DataFrame, config: dict) -> str:
    col = first_existing_column(meta, config["metadata"]["marker_columns"]["possible_sample"])
    if col:
        return col
    for candidate in meta.columns:
        values = meta[candidate].astype(str)
        if values.str.contains(r"^(LUNG|EBUS|BRONCHO|LN|EFFUSION|NS)_", regex=True).mean() > 0.5:
            return candidate
    raise ValueError(f"Could not infer sample column from columns: {meta.columns.tolist()}")


def infer_celltype_column(meta: pd.DataFrame, config: dict) -> str:
    col = first_existing_column(meta, config["metadata"]["marker_columns"]["possible_celltype"])
    if col:
        return col
    categorical = [col for col in meta.columns if meta[col].nunique(dropna=True) < 100]
    if categorical:
        return categorical[-1]
    raise ValueError(f"Could not infer cell-type column from columns: {meta.columns.tolist()}")


def infer_tissue_site(sample: str) -> str:
    sample = str(sample)
    if sample.startswith("LUNG_N"):
        return "normal_lung"
    if sample.startswith("LUNG_T"):
        return "primary_tumor"
    if sample.startswith("EBUS") or sample.startswith("BRONCHO"):
        return "advanced_airway_tumor"
    if sample.startswith("LN_"):
        return "normal_lymph_node"
    if sample.startswith("EFFUSION"):
        return "pleural_effusion"
    if sample.startswith("NS_"):
        return "non_smoker_lung"
    return "other"


def infer_patient_id(sample: str) -> str:
    sample = str(sample)
    match = re.search(r"(\d+)$", sample)
    return match.group(1) if match else sample
