"""Qlib factor runner for mini1: full-sample factor compute, trimmed parquet for backtest."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import List

import pandas as pd

try:
    from pandarallel import pandarallel

    pandarallel.initialize(verbose=0)
except Exception:
    pass

from quantaalpha.components.runner import CachedRunner
from quantaalpha.core.conf import RD_AGENT_SETTINGS
from quantaalpha.core.exception import FactorEmptyError
from quantaalpha.core.utils import cache_with_pickle, multiprocessing_wrapper
from quantaalpha.factors.backtest_export import save_backtest_parquet
from quantaalpha.factors.experiment import QlibFactorExperiment
from quantaalpha.log import logger

DIRNAME = Path(__file__).absolute().resolve().parent


class QlibFactorRunner(CachedRunner[QlibFactorExperiment]):
    def __init__(self, scen=None) -> None:
        self.scen = scen

    def calculate_information_coefficient(
        self,
        concat_feature: pd.DataFrame,
        sota_feature_column_size: int,
        new_feature_columns_size: int,
    ) -> pd.Series:
        res = pd.Series(index=range(sota_feature_column_size * new_feature_columns_size))
        for col1 in range(sota_feature_column_size):
            for col2 in range(
                sota_feature_column_size,
                sota_feature_column_size + new_feature_columns_size,
            ):
                res.loc[col1 * new_feature_columns_size + col2 - sota_feature_column_size] = (
                    concat_feature.iloc[:, col1].corr(concat_feature.iloc[:, col2])
                )
        return res

    def deduplicate_new_factors(
        self, sota_feature: pd.DataFrame, new_feature: pd.DataFrame
    ) -> pd.DataFrame:
        concat_feature = pd.concat([sota_feature, new_feature], axis=1)
        ic_max = (
            concat_feature.groupby("datetime")
            .parallel_apply(
                lambda x: self.calculate_information_coefficient(
                    x, sota_feature.shape[1], new_feature.shape[1]
                )
            )
            .mean()
        )
        ic_max.index = pd.MultiIndex.from_product(
            [range(sota_feature.shape[1]), range(new_feature.shape[1])]
        )
        ic_max = ic_max.unstack().max(axis=0)
        return new_feature.iloc[:, ic_max[ic_max < 0.99].index]

    def process_factor_data(
        self, exp_or_list: List[QlibFactorExperiment] | QlibFactorExperiment
    ) -> pd.DataFrame:
        if isinstance(exp_or_list, QlibFactorExperiment):
            exp_or_list = [exp_or_list]
        factor_dfs: list[pd.DataFrame] = []

        for exp in exp_or_list:
            if not exp.sub_workspace_list:
                continue
            message_and_df_list = multiprocessing_wrapper(
                [
                    (implementation.execute, ("All",))
                    for implementation in exp.sub_workspace_list
                ],
                n=RD_AGENT_SETTINGS.multi_proc_n,
            )
            for idx, (message, df) in enumerate(message_and_df_list):
                if df is None or "datetime" not in getattr(df.index, "names", []):
                    logger.warning(
                        f"Factor data not generated for workspace {idx}: {message}"
                    )
                    continue
                time_diff = (
                    df.index.get_level_values("datetime")
                    .to_series()
                    .diff()
                    .dropna()
                    .unique()
                )
                if pd.Timedelta(minutes=1) not in time_diff:
                    if isinstance(df, pd.Series):
                        name = getattr(
                            exp.sub_workspace_list[idx].target_task,
                            "factor_name",
                            None,
                        ) or df.name or f"factor_{idx}"
                        df = df.to_frame(name=name)
                    factor_dfs.append(df)

        if factor_dfs:
            return pd.concat(factor_dfs, axis=1)
        raise FactorEmptyError("No valid factor data found to merge.")

    def _manual_execute_factors(self, exp: QlibFactorExperiment) -> None:
        from quantaalpha.factors.mini1_train_loader import train_parquet_path

        train_path = train_parquet_path()
        for ws in exp.sub_workspace_list:
            result_h5 = ws.workspace_path / "result.h5"
            if result_h5.exists():
                continue
            train_link = ws.workspace_path / "train.parquet"
            if not train_link.exists() and train_path.exists():
                os.symlink(str(train_path), str(train_link))
            fp = (ws.workspace_path / "factor.py").resolve()
            if not fp.exists():
                continue
            env = os.environ.copy()
            project_root = Path(__file__).resolve().parents[2]
            env["PYTHONPATH"] = f"{project_root}{os.pathsep}{env.get('PYTHONPATH', '')}"
            try:
                subprocess.check_output(
                    [sys.executable, str(fp)],
                    cwd=str(ws.workspace_path.resolve()),
                    stderr=subprocess.STDOUT,
                    timeout=3600,
                )
            except subprocess.CalledProcessError as exc:
                logger.warning(f"Failed to manually execute factor {fp}: {exc}")

    @cache_with_pickle(CachedRunner.get_cache_key, CachedRunner.assign_cached_result)
    def develop(self, exp: QlibFactorExperiment, use_local: bool = True) -> QlibFactorExperiment:
        if not exp.sub_workspace_list:
            raise FactorEmptyError(
                "No factor implementations in this experiment; skip backtest."
            )

        sota_factor = None
        if exp.based_experiments and len(exp.based_experiments) > 0:
            sota_exps = [
                base_exp
                for base_exp in exp.based_experiments
                if isinstance(base_exp, QlibFactorExperiment) and base_exp.sub_workspace_list
            ]
            if len(sota_exps) > 1:
                try:
                    sota_factor = self.process_factor_data(sota_exps)
                except FactorEmptyError:
                    logger.warning(
                        "SOTA factors processing failed, continuing with new factors only."
                    )

        try:
            new_factors = self.process_factor_data(exp)
        except FactorEmptyError as e:
            logger.error(f"Failed to process new factors: {e}")
            logger.info("Attempting to manually execute factors...")
            self._manual_execute_factors(exp)
            new_factors = self.process_factor_data(exp)

        if new_factors.empty:
            raise FactorEmptyError("No valid factor data found to merge.")

        if sota_factor is not None and not sota_factor.empty:
            new_factors = self.deduplicate_new_factors(sota_factor, new_factors)
            if new_factors.empty:
                raise FactorEmptyError(
                    "New factors are highly similar to SOTA; change the mining direction."
                )
            combined_factors = pd.concat([sota_factor, new_factors], axis=1).dropna()
        else:
            combined_factors = new_factors

        combined_factors = combined_factors.sort_index()
        combined_factors = combined_factors.loc[
            :, ~combined_factors.columns.duplicated(keep="last")
        ]

        with pd.option_context("display.width", 200):
            try:
                corr = combined_factors.groupby("datetime").corr().mean()
                logger.info(f"Factor correlation: \n\n{corr}\n")
            except Exception:
                pass

        logger.info(f"Factor values this round: \n\n{combined_factors.tail()}\n\n")

        parquet_path = exp.experiment_workspace.workspace_path / "combined_factors_df.parquet"
        save_backtest_parquet(combined_factors, parquet_path)
        size_mb = parquet_path.stat().st_size / (1024 * 1024)
        logger.info(f"Saved combined factors to {parquet_path} ({size_mb:.1f} MB)")

        config_name = os.environ.get("QA_QLIB_CONF", "").strip() or "conf_mini1_smoke50.yaml"

        logger.info(
            f"Execute factor backtest (Use {'Local' if use_local else 'Docker container'}): "
            f"{config_name} (mini1 smoke backtest)"
        )
        exp.experiment_workspace.before_execute()
        result_tuple = exp.experiment_workspace.execute(
            qlib_config_name=config_name,
            run_env={},
        )

        if isinstance(result_tuple, tuple):
            result = result_tuple[0] if len(result_tuple) > 0 else None
            stdout = result_tuple[1] if len(result_tuple) > 1 else ""
        else:
            result, stdout = result_tuple, ""

        if result is not None:
            preview = result.iloc[2:] if hasattr(result, "iloc") else result
            logger.info(f"Backtesting results: \n{preview}")
        else:
            logger.warning(
                "Backtesting result is None. Check the execution logs above for errors."
            )
            if stdout:
                logger.info(f"Execution log: {stdout[:500]}...")
            raise FactorEmptyError(
                f"Factor backtest failed; see logs above. Last stdout: {str(stdout)[:300]}"
            )

        exp.result = result
        exp.stdout = stdout if isinstance(stdout, str) else str(stdout)
        return exp
