"""
QuantaAlpha custom workspace.

Overrides rdagent QlibFBWorkspace: project-level factor_template overrides default YAML;
runs qrun via LocalEnv (no conda); reads qlib_res.csv for metrics.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from rdagent.log import rdagent_logger as logger
from rdagent.scenarios.qlib.experiment.workspace import QlibFBWorkspace as _RdagentQlibFBWorkspace
from rdagent.utils.env import LocalConf, LocalEnv

_CUSTOM_TEMPLATE_DIR = Path(__file__).resolve().parent / "factor_template"
_DEFAULT_BIN_DIR = "/srv/quant/envs/quantsociety_backend/bin"


def _qlib_run_env(extra: dict | None = None) -> dict[str, str]:
    bin_dir = os.environ.get("QUANTA_BIN_DIR", _DEFAULT_BIN_DIR)
    env = {**os.environ, **(extra or {})}
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
    qlib_data = os.environ.get(
        "QLIB_DATA_DIR",
        os.environ.get(
            "QLIB_PROVIDER_URI",
            str(Path("~/.qlib/qlib_data/cn_data").expanduser()),
        ),
    )
    env["QLIB_DATA_DIR"] = qlib_data
    env["QLIB_PROVIDER_URI"] = qlib_data
    env.setdefault("OMP_NUM_THREADS", os.environ.get("OMP_NUM_THREADS", "4"))
    return env


class QlibFBWorkspace(_RdagentQlibFBWorkspace):
    """
    Override rdagent QlibFBWorkspace: inject project factor_template/ YAML over defaults;
    init empty git repo in workspace to avoid qlib recorder git help output.
    """

    def __init__(self, template_folder_path: Path, *args, **kwargs) -> None:
        super().__init__(template_folder_path, *args, **kwargs)
        if _CUSTOM_TEMPLATE_DIR.exists():
            self.inject_code_from_folder(_CUSTOM_TEMPLATE_DIR)
            logger.info(f"Overrode rdagent default config with project template: {_CUSTOM_TEMPLATE_DIR}")

    def before_execute(self) -> None:
        super().before_execute()
        git_dir = self.workspace_path / ".git"
        if git_dir.exists():
            return
        try:
            subprocess.run(
                ["git", "init"],
                cwd=str(self.workspace_path),
                capture_output=True,
                timeout=5,
                check=False,
            )
        except Exception:
            pass

    def execute(
        self,
        qlib_config_name: str = "conf.yaml",
        run_env: dict | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[Any, str]:
        if run_env is None:
            run_env = {}
        merged_env = _qlib_run_env(run_env)
        bin_dir = os.environ.get("QUANTA_BIN_DIR", _DEFAULT_BIN_DIR)
        qtde = LocalEnv(conf=LocalConf(bin_path=bin_dir, default_entry="qrun conf.yaml", enable_cache=False))
        qtde.prepare()

        execute_qlib_log = qtde.check_output(
            local_path=str(self.workspace_path),
            entry=f"qrun {qlib_config_name}",
            env=merged_env,
        )
        logger.log_object(execute_qlib_log, tag="Qlib_execute_log")

        execute_log = qtde.check_output(
            local_path=str(self.workspace_path),
            entry="python read_exp_res.py",
            env=merged_env,
        )

        ret_pkl = self.workspace_path / "ret.pkl"
        if ret_pkl.exists():
            ret_df = pd.read_pickle(ret_pkl)
            logger.log_object(ret_df, tag="Quantitative Backtesting Chart")
        else:
            qlib_res_path = self.workspace_path / "qlib_res.csv"
            if qlib_res_path.exists():
                pattern = r"(Epoch\d+: train -[0-9\.]+, valid -[0-9\.]+|best score: -[0-9\.]+ @ \d+ epoch)"
                matches = re.findall(pattern, execute_qlib_log)
                execute_qlib_log = "\n".join(matches)
                return pd.read_csv(qlib_res_path, index_col=0).iloc[:, 0], execute_qlib_log

            logger.error("No result file found.")
            return None, execute_qlib_log

        qlib_res_path = self.workspace_path / "qlib_res.csv"
        if qlib_res_path.exists():
            pattern = r"(Epoch\d+: train -[0-9\.]+, valid -[0-9\.]+|best score: -[0-9\.]+ @ \d+ epoch)"
            matches = re.findall(pattern, execute_qlib_log)
            execute_qlib_log = "\n".join(matches)
            return pd.read_csv(qlib_res_path, index_col=0).iloc[:, 0], execute_qlib_log

        logger.error(f"File {qlib_res_path} does not exist.")
        return None, execute_qlib_log
