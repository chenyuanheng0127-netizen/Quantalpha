"""Factor execution panel sourced only from mini1/train.parquet."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

from quantaalpha.factors.coder.expr_parser import parse_expression, parse_symbol

_DEFAULT_TRAIN = (
    "/home/ubuntu/chenyuanhengWorkspace/MAFS5140-Spring2026-Project/mini1/train.parquet"
)


def train_parquet_path() -> Path:
    return Path(os.environ.get("MINI1_TRAIN_PARQUET", _DEFAULT_TRAIN))


def _sym_panel(wide: pd.DataFrame, sym: str) -> pd.DataFrame:
    sub = wide[sym].copy()
    close = sub["close"].astype(np.float64)
    vol = sub["volume"].astype(np.float64)
    open_ = close.shift(1).fillna(close)
    high = pd.concat([open_, close], axis=1).max(axis=1)
    low = pd.concat([open_, close], axis=1).min(axis=1)
    panel = pd.DataFrame(
        {
            "$open": open_,
            "$high": high,
            "$low": low,
            "$close": close,
            "$return": close.pct_change().fillna(0.0),
            "$volume": vol,
        },
        index=wide.index,
    )
    return panel


def _build_long_panel(wide: pd.DataFrame) -> pd.DataFrame:
    chunks: list[pd.DataFrame] = []
    tickers = list(wide.columns.get_level_values(0).unique())
    for sym in tickers:
        panel = _sym_panel(wide, sym)
        if panel["$close"].notna().sum() == 0:
            continue
        panel.index = pd.MultiIndex.from_product(
            [panel.index, [sym]], names=["datetime", "instrument"]
        )
        chunks.append(panel)

    if not chunks:
        raise ValueError("No valid symbol panels found in train.parquet")
    return pd.concat(chunks).sort_index()


def _eval_on_panel(panel: pd.DataFrame, expr: str, name: str) -> pd.Series:
    from quantaalpha.factors.coder import function_lib  # noqa: WPS433

    expr = parse_symbol(expr, panel.columns)
    expr = parse_expression(expr)
    local_df = panel
    for col in panel.columns:
        expr = expr.replace(col[1:], f"local_df['{col}']")
    values = eval(expr, {"__builtins__": {}}, {**function_lib.__dict__, "local_df": local_df})
    if isinstance(values, pd.DataFrame):
        values = values.iloc[:, 0]
    return pd.Series(values, index=panel.index, name=name, dtype=np.float64)


def compute_factor_from_train(expr: str, name: str) -> pd.Series:
    path = train_parquet_path()
    if not path.exists():
        raise FileNotFoundError(f"MINI1 train.parquet not found: {path}")

    wide = pd.read_parquet(path)
    if wide.index.tz is not None:
        wide = wide.copy()
        wide.index = wide.index.tz_convert("UTC").tz_localize(None)

    panel = _build_long_panel(wide)
    out = _eval_on_panel(panel, expr, name).sort_index()
    if "ZSCORE(" in expr and "TS_ZSCORE" not in expr:
        out = out.groupby(level="datetime", group_keys=False).transform(
            lambda x: (x - x.mean()) / (x.std(ddof=0) + 1e-12)
        )
    return out.astype(np.float64)
