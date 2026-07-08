from __future__ import annotations

import pandas as pd

from common import (
    DATA_METADATA,
    DATA_RAW,
    RESULTS_TABLES,
    ensure_dirs,
    infer_celltype_column,
    infer_patient_id,
    infer_sample_column,
    infer_tissue_site,
    load_config,
)


def main() -> None:
    ensure_dirs()
    config = load_config()
    annotation_path = DATA_RAW / config["files"]["annotation"]
    if not annotation_path.exists():
        raise FileNotFoundError(f"Missing {annotation_path}. Run scripts/00_download_geo.py --annotation-only first.")

    meta = pd.read_csv(annotation_path, sep="\t", compression="gzip")
    sample_col = infer_sample_column(meta, config)
    celltype_col = infer_celltype_column(meta, config)

    out = meta.copy()
    out["sample"] = out[sample_col].astype(str)
    out["patient_id"] = out["sample"].map(infer_patient_id)
    out["tissue_site"] = out["sample"].map(infer_tissue_site)
    out["cell_type_clean"] = out[celltype_col].astype(str)

    out.to_csv(DATA_METADATA / "gse131907_cell_metadata_clean.csv", index=False)

    sample_meta = (
        out[["sample", "patient_id", "tissue_site"]]
        .drop_duplicates()
        .sort_values(["tissue_site", "sample"])
    )
    sample_meta.to_csv(DATA_METADATA / "sample_metadata_clean.csv", index=False)
    sample_meta.to_csv(RESULTS_TABLES / "sample_metadata_clean.csv", index=False)

    print(f"Annotation shape: {meta.shape}")
    print(f"Sample column: {sample_col}")
    print(f"Cell type column: {celltype_col}")
    print(sample_meta.head(20).to_string(index=False))


if __name__ == "__main__":
    main()

