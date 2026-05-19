"""Export Qlib backtest parquet (trimmed) without shrinking factor-mining compute scope."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml

_TEMPLATE_DIR = Path(__file__).resolve().parent / "factor_template"
_DEFAULT_CONF = "conf_mini1_smoke50.yaml"
_QLIB_INSTR_DIR = Path(
    os.environ.get(
        "QLIB_DATA_DIR",
        "/home/ubuntu/chenyuanhengWorkspace/QuantaAlpha/data/qlib/mini1_us_5min",
    )
) / "instruments"


def _conf_path(config_name: str | None = None) -> Path:
    name = (config_name or os.environ.get("QA_QLIB_CONF", "") or _DEFAULT_CONF).strip()
    if not name:
        name = _DEFAULT_CONF
    p = _TEMPLATE_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Qlib config not found: {p}")
    return p


def load_qlib_backtest_window(config_name: str | None = None) -> tuple[pd.Timestamp, pd.Timestamp, str]:
    cfg = yaml.safe_load(_conf_path(config_name).read_text())
    handler = cfg["task"]["dataset"]["kwargs"]["handler"]["kwargs"]
    start = pd.Timestamp(handler["start_time"])
    end = pd.Timestamp(handler["end_time"])
    market = handler["instruments"]
    if isinstance(market, str) and market.startswith("&"):
        market = cfg.get("market", market.lstrip("&"))
    return start, end, str(market)


def load_smoke50_symbols(market: str = "mini1_smoke50") -> list[str]:
    inst_file = _QLIB_INSTR_DIR / f"{market}.txt"
    if not inst_file.exists():
        raise FileNotFoundError(
            f"Instrument list missing: {inst_file}. Run scripts/build_mini1_smoke50_instruments.py"
        )
    symbols: list[str] = []
    for line in inst_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        symbols.append(line.split()[0])
    return symbols


def _normalize_factor_frame(combined: pd.DataFrame) -> pd.DataFrame:
    df = combined.copy()
    if not isinstance(df.index, pd.MultiIndex) or df.index.nlevels < 2:
        raise ValueError("combined factors must have MultiIndex (datetime, instrument)")
    if df.index.names[0] != "datetime":
        df.index = df.index.set_names(["datetime", "instrument"])
    if isinstance(df.columns, pd.MultiIndex):
        if "feature" in df.columns.get_level_values(0):
            df.columns = df.columns.get_level_values(1)
        else:
            df.columns = df.columns.get_level_values(-1)
    if df.index.get_level_values("datetime").tz is not None:
        dt = df.index.get_level_values("datetime").tz_convert("UTC").tz_localize(None)
        df.index = pd.MultiIndex.from_arrays(
            [dt, df.index.get_level_values("instrument")],
            names=["datetime", "instrument"],
        )
    return df.sort_index()


def trim_for_qlib_backtest(
    combined: pd.DataFrame,
    *,
    config_name: str | None = None,
    symbols: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Subset + downcast for Qlib StaticDataLoader; full `combined` is unchanged in memory."""
    start, end, market = load_qlib_backtest_window(config_name)
    syms = list(symbols) if symbols is not None else load_smoke50_symbols(market)
    sym_set = set(syms)

    df = _normalize_factor_frame(combined)
    dt_idx = df.index.get_level_values("datetime")
    mask = (dt_idx >= start) & (dt_idx <= end) & df.index.get_level_values("instrument").isin(sym_set)
    out = df.loc[mask]
    if out.empty:
        raise ValueError(
            f"No factor rows after trim (symbols={len(sym_set)}, {start}..{end}). "
            "Check mini1_smoke50 instruments and factor datetime index."
        )
    return out.astype("float32")


def save_backtest_parquet(
    combined: pd.DataFrame,
    target_path: Path,
    *,
    config_name: str | None = None,
) -> Path:
    trimmed = trim_for_qlib_backtest(combined, config_name=config_name)
    nested = trimmed.copy()
    nested.columns = pd.MultiIndex.from_product([["feature"], nested.columns])
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    nested.to_parquet(target_path, engine="pyarrow", compression="zstd")
    size_mb = target_path.stat().st_size / (1024 * 1024)
    return target_path
