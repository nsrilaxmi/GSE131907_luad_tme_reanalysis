from __future__ import annotations

from pathlib import Path

import pandas as pd

from common import DOCS_TABLES, RESULTS_TABLES, ensure_dirs
from signatures import SIGNATURES


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
