#!/usr/bin/env python3
"""
Convert MAFS5140 mini1 parquet (5-min OHLCV) to Qlib binary format (freq=5min).

Output layout:
  <qlib_dir>/calendars/5min.txt
  <qlib_dir>/instruments/all.txt
  <qlib_dir>/features/<symbol>/{open,high,low,close,volume,factor}.5min.bin
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DUMP_BIN_URL = (
    "https://raw.githubusercontent.com/microsoft/qlib/v0.9.7/scripts/dump_bin.py"
)


def _normalize_index(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    if idx.tz is not None:
        idx = idx.tz_convert("UTC").tz_localize(None)
    return pd.DatetimeIndex(idx).sort_values()


def _ohlcv_from_ticker_block(sub: pd.DataFrame) -> pd.DataFrame:
    """Build OHLCV; synthesize open/high/low when parquet only has close+volume."""
    close = sub["close"].astype(np.float64)
    vol = sub["volume"].astype(np.float64)
    if "open" in sub.columns and "high" in sub.columns and "low" in sub.columns:
        open_ = sub["open"].astype(np.float64)
        high = sub["high"].astype(np.float64)
        low = sub["low"].astype(np.float64)
    else:
        open_ = close.shift(1).fillna(close)
        high = pd.concat([open_, close], axis=1).max(axis=1)
        low = pd.concat([open_, close], axis=1).min(axis=1)
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": vol})


def h5_to_symbol_csvs(h5_path: Path, csv_dir: Path, max_symbols: int | None = None) -> list[str]:
    """Convert QuantaAlpha-style daily_pv.h5 (MultiIndex, $fields) to per-symbol CSVs."""
    csv_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_hdf(h5_path, key="data")
    df = df.rename(columns=lambda c: c.lstrip("$"))
    df.index = df.index.set_names(["datetime", "instrument"])
    df = df.reset_index()
    df["datetime"] = _normalize_index(pd.DatetimeIndex(df["datetime"]))

    symbols = sorted(df["instrument"].unique())
    if max_symbols is not None:
        symbols = symbols[:max_symbols]

    written: list[str] = []
    for sym in symbols:
        sub = df[df["instrument"] == sym].set_index("datetime")
        ohlcv = _ohlcv_from_ticker_block(sub)
        out = ohlcv.reset_index().rename(columns={"datetime": "date"})
        out["factor"] = 1.0
        out = out.dropna(subset=["close"])
        if out.empty:
            continue
        out = out.drop_duplicates(subset=["date"], keep="last")
        out.to_csv(csv_dir / f"{str(sym).lower()}.csv", index=False)
        written.append(str(sym))
    print(f"From H5: wrote {len(written)} CSVs")
    return written


def wide_parquet_to_symbol_csvs(
    parquet_paths: list[Path],
    csv_dir: Path,
    max_symbols: int | None = None,
) -> list[str]:
    """Write one CSV per symbol: date,open,high,low,close,volume,factor."""
    csv_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for p in parquet_paths:
        if not p.exists():
            raise FileNotFoundError(p)
        print(f"Loading {p} ...")
        frames.append(pd.read_parquet(p))
    wide = pd.concat(frames, axis=0)
    wide = wide[~wide.index.duplicated(keep="last")]
    wide = wide.sort_index()
    wide.index = _normalize_index(pd.DatetimeIndex(wide.index))

    if not isinstance(wide.columns, pd.MultiIndex):
        raise ValueError("Expected MultiIndex columns (ticker, field)")

    sym_level = 0
    if wide.columns.names and wide.columns.names[0]:
        sym_level = wide.columns.names.index(wide.columns.names[0]) if "ticker" in wide.columns.names else 0

    symbols = list(wide.columns.get_level_values(sym_level).unique())
    if max_symbols is not None:
        symbols = symbols[: max_symbols]

    written: list[str] = []
    for sym in symbols:
        sub = wide[sym] if sym in wide.columns.get_level_values(0) else wide.xs(sym, axis=1, level=0)
        if "close" not in sub.columns or "volume" not in sub.columns:
            continue
        ohlcv = _ohlcv_from_ticker_block(sub)
        out = ohlcv.copy()
        out.index.name = "date"
        out = out.reset_index()
        out["factor"] = 1.0
        out = out.dropna(subset=["close"])
        if out.empty:
            continue
        out = out.drop_duplicates(subset=["date"], keep="last")
        out.to_csv(csv_dir / f"{str(sym).lower()}.csv", index=False)
        written.append(str(sym))

    print(f"Wrote {len(written)} symbol CSVs -> {csv_dir}")
    return written


def ensure_dump_bin(script_dir: Path) -> Path:
    target = script_dir / "dump_bin.py"
    if not target.exists():
        import urllib.request

        print(f"Downloading dump_bin.py -> {target}")
        urllib.request.urlretrieve(DUMP_BIN_URL, target)
    return target


def run_dump_all(
    dump_bin: Path,
    csv_dir: Path,
    qlib_dir: Path,
    freq: str = "5min",
    max_workers: int = 8,
) -> None:
    qlib_dir = qlib_dir.expanduser().resolve()
    if qlib_dir.exists():
        shutil.rmtree(qlib_dir)
    qlib_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        str(dump_bin),
        "dump_all",
        "--data_path",
        str(csv_dir),
        "--qlib_dir",
        str(qlib_dir),
        "--freq",
        freq,
        "--date_field_name",
        "date",
        "--file_suffix",
        ".csv",
        "--include_fields",
        "open,high,low,close,volume,factor",
        "--max_workers",
        str(max_workers),
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    inst_all = qlib_dir / "instruments" / "all.txt"
    inst_mini1 = qlib_dir / "instruments" / "mini1.txt"
    if inst_all.exists():
        shutil.copy2(inst_all, inst_mini1)

    cal_5 = qlib_dir / "calendars" / f"{freq}.txt"
    if cal_5.exists():
        shutil.copy2(cal_5, qlib_dir / "calendars" / "1min.txt")
        days = sorted({ln.split()[0] for ln in cal_5.read_text().splitlines() if ln.strip()})
        (qlib_dir / "calendars" / "day.txt").write_text("\n".join(days) + "\n", encoding="utf-8")
    features_root = qlib_dir / "features"
    if features_root.is_dir():
        for inst_dir in features_root.iterdir():
            if not inst_dir.is_dir():
                continue
            for bin_path in inst_dir.glob(f"*.{freq}.bin"):
                alias = bin_path.with_name(bin_path.name.replace(f".{freq}.bin", ".1min.bin"))
                if not alias.exists():
                    shutil.copy2(bin_path, alias)

    print(f"Qlib mini1 5min data ready: {qlib_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Qlib 5min dataset from mini1 parquet")
    parser.add_argument("--proj", default=".", help="Project root containing mini1/")
    parser.add_argument("--qlib-dir", default="./data/qlib/mini1_us_5min", help="Output Qlib provider directory")
    parser.add_argument("--csv-dir", default="./mini1_qlib_csv", help="Temporary per-symbol CSV directory")
    parser.add_argument("--max-symbols", type=int, default=None, help="Limit symbols (for quick test)")
    parser.add_argument("--h5", default=None, help="Optional daily_pv.h5 (full OHLCV).")
    parser.add_argument("--skip-csv", action="store_true", help="Reuse existing CSV dir, only run dump_bin")
    parser.add_argument("--max-workers", type=int, default=8)
    args = parser.parse_args()

    proj = Path(args.proj)
    parquet_paths = [proj / "mini1" / "train.parquet", proj / "mini1" / "validation.parquet"]
    h5_path = Path(args.h5) if args.h5 else proj / "mini1_h5" / "daily_pv.h5"
    csv_dir = Path(args.csv_dir)
    qlib_dir = Path(args.qlib_dir)
    script_dir = Path(__file__).resolve().parent

    if not args.skip_csv:
        if csv_dir.exists():
            shutil.rmtree(csv_dir)
        if h5_path.exists():
            h5_to_symbol_csvs(h5_path, csv_dir, max_symbols=args.max_symbols)
        wide_parquet_to_symbol_csvs(parquet_paths, csv_dir, max_symbols=args.max_symbols)

    dump_bin = ensure_dump_bin(script_dir)
    run_dump_all(dump_bin, csv_dir, qlib_dir, max_workers=args.max_workers)


if __name__ == "__main__":
    main()
