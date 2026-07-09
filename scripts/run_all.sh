#!/usr/bin/env bash
set -euo pipefail

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/gse131907_mpl}"
export NUMBA_CACHE_DIR="${NUMBA_CACHE_DIR:-/tmp/gse131907_numba}"

PYTHON_BIN="${PYTHON_BIN:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "No Python interpreter found." >&2
    exit 1
  fi
fi

"$PYTHON_BIN" scripts/01_metadata_overview.py
"$PYTHON_BIN" scripts/02_composition_analysis.py
"$PYTHON_BIN" scripts/03_signature_plan.py

if [[ "${1:-}" == "--with-expression" ]]; then
  "$PYTHON_BIN" scripts/04_signature_scoring.py
  "$PYTHON_BIN" scripts/05_signature_statistics.py
  "$PYTHON_BIN" scripts/06_subtype_analysis.py
  "$PYTHON_BIN" scripts/07_paired_patient_analysis.py
  "$PYTHON_BIN" scripts/09_key_results_summary.py
  "$PYTHON_BIN" scripts/10_signature_score_sensitivity.py
fi
