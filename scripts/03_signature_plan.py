from __future__ import annotations

from pathlib import Path

import pandas as pd

from common import DOCS_TABLES, RESULTS_TABLES, ensure_dirs


SIGNATURES = {
    "T_CELL_EXHAUSTION": ["PDCD1", "CTLA4", "LAG3", "HAVCR2", "TIGIT", "TOX"],
    "CYTOTOXICITY": ["GZMB", "GZMA", "PRF1", "NKG7", "GNLY", "IFNG"],
    "MYELOID_INFLAMMATION": ["IL1B", "TNF", "CXCL8", "S100A8", "S100A9", "FCN1"],
    "MACROPHAGE_LIKE": ["APOE", "C1QA", "C1QB", "MRC1", "MARCO", "CD163"],
    "EMT_INVASION": ["VIM", "ZEB1", "ZEB2", "SNAI1", "SNAI2", "ITGA5", "COL1A1"],
    "HYPOXIA": ["VEGFA", "CA9", "SLC2A1", "LDHA", "ENO1", "BNIP3"],
    "PROLIFERATION": ["MKI67", "TOP2A", "PCNA", "STMN1", "UBE2C", "HMGB2"],
}


def main() -> None:
    ensure_dirs()
    rows = []
    for signature, genes in SIGNATURES.items():
        for gene in genes:
            rows.append({"signature": signature, "gene": gene})
    df = pd.DataFrame(rows)
    for path in [RESULTS_TABLES / "planned_tme_signatures.csv", DOCS_TABLES / "planned_tme_signatures.csv"]:
        df.to_csv(path, index=False)
    print(f"Wrote {len(SIGNATURES)} planned TME signatures.")


if __name__ == "__main__":
    main()

