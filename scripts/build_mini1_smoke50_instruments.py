#!/usr/bin/env python3
"""Build mini1_smoke50 Qlib instrument list (first 50 tickers in mini1.txt)."""

from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_QLIB = Path("/home/ubuntu/chenyuanhengWorkspace/QuantaAlpha/data/qlib/mini1_us_5min")
DEFAULT_N = 50


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qlib-dir", type=Path, default=DEFAULT_QLIB)
    parser.add_argument("--n", type=int, default=DEFAULT_N)
    args = parser.parse_args()

    src = args.qlib_dir / "instruments" / "mini1.txt"
    dst = args.qlib_dir / "instruments" / "mini1_smoke50.txt"
    if not src.exists():
        raise SystemExit(f"Missing {src}")

    lines = [ln.strip() for ln in src.read_text().splitlines() if ln.strip()]
    picked = lines[: args.n]
    dst.write_text("\n".join(picked) + "\n")
    print(f"Wrote {len(picked)} instruments -> {dst}")


if __name__ == "__main__":
    main()
