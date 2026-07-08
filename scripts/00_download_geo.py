from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

from common import DATA_RAW, ensure_dirs, load_config


def download(url: str, output: Path) -> None:
    if output.exists() and output.stat().st_size > 0:
        print(f"Already present: {output.name}")
        return
    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotation-only", action="store_true", help="Download only the lightweight annotation file.")
    parser.add_argument(
        "--raw-only",
        action="store_true",
        help="Download annotation, raw UMI matrix, and feature summary; skip the very large normalized log2TPM matrix.",
    )
    args = parser.parse_args()

    ensure_dirs()
    config = load_config()
    if args.annotation_only:
        files = ["annotation"]
    elif args.raw_only:
        files = ["annotation", "raw_umi_txt", "feature_summary"]
    else:
        files = list(config["files"].keys())
    for key in files:
        filename = config["files"][key]
        download(f"{config['geo_base_url']}/{filename}", DATA_RAW / filename)


if __name__ == "__main__":
    main()
