"""
QuantaAlpha factor experiment module: Scenario and Experiment classes.

Uses project QlibFBWorkspace (no conda) and mini1 factor_template YAML.
"""

from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path

from rdagent.components.coder.factor_coder.config import get_factor_env
from rdagent.components.coder.factor_coder.factor import FactorExperiment, FactorFBWorkspace, FactorTask
from rdagent.core.experiment import Task
from rdagent.core.scenario import Scenario
from rdagent.scenarios.qlib.experiment.factor_experiment import QlibFactorExperiment as _OrigQlibFactorExperiment
from rdagent.scenarios.qlib.experiment.utils import get_data_folder_intro
from rdagent.scenarios.shared.get_runtime_info import get_runtime_environment_by_env
from rdagent.utils.agent.tpl import T

from quantaalpha.factors.workspace import QlibFBWorkspace

_TEMPLATE_DIR = Path(__file__).resolve().parent / "factor_template"


class QlibFactorExperiment(_OrigQlibFactorExperiment):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.experiment_workspace = QlibFBWorkspace(template_folder_path=_TEMPLATE_DIR)
        self.stdout = ""


class QlibFactorScenario(Scenario):
    """Qlib factor scenario without Docker data-folder bootstrap (mini1 local path)."""

    def __init__(self, use_local: bool = True) -> None:
        super().__init__()
        self.use_local = use_local
        self._background = deepcopy(
            T(".prompts:qlib_factor_background").r(runtime_environment=self.get_runtime_environment())
        )
        train_path = os.environ.get(
            "MINI1_TRAIN_PARQUET",
            "/home/ubuntu/chenyuanhengWorkspace/MAFS5140-Spring2026-Project/mini1/train.parquet",
        )
        qlib_uri = os.environ.get(
            "QLIB_PROVIDER_URI",
            "/home/ubuntu/chenyuanhengWorkspace/QuantaAlpha/data/qlib/mini1_us_5min",
        )
        if use_local:
            self._source_data = (
                f"5-minute US panel from train.parquet ({train_path}). "
                f"Use $volume, $return, and related columns. "
                f"Qlib smoke backtest provider: {qlib_uri}."
            )
        else:
            self._source_data = deepcopy(get_data_folder_intro())
        self._output_format = deepcopy(T(".prompts:qlib_factor_output_format").r())
        self._interface = deepcopy(T(".prompts:qlib_factor_interface").r())
        self._strategy = deepcopy(T(".prompts:qlib_factor_strategy").r())
        self._simulator = deepcopy(T(".prompts:qlib_factor_simulator").r())
        self._rich_style_description = deepcopy(T(".prompts:qlib_factor_rich_style_description").r())
        self._experiment_setting = deepcopy(T(".prompts:qlib_factor_experiment_setting").r())

    @property
    def background(self) -> str:
        return self._background

    def get_source_data_desc(self, task: Task | None = None) -> str:
        return self._source_data

    @property
    def output_format(self) -> str:
        return self._output_format

    @property
    def interface(self) -> str:
        return self._interface

    @property
    def simulator(self) -> str:
        return self._simulator

    @property
    def rich_style_description(self) -> str:
        return self._rich_style_description

    @property
    def experiment_setting(self) -> str:
        return self._experiment_setting

    def get_scenario_all_desc(
        self, task: Task | None = None, filtered_tag: str | None = None, simple_background: bool | None = None
    ) -> str:
        if simple_background:
            return f"""Background of the scenario:
{self.background}"""
        return f"""Background of the scenario:
{self.background}
The source data you can use:
{self.get_source_data_desc(task)}
The interface you should follow to write the runnable code:
{self.interface}
The output of your code should be in the format:
{self.output_format}
The simulator can help you to understand the factor:
{self.simulator}
The experiment setting is as follows:
{self.experiment_setting}
"""

    def get_runtime_environment(self) -> str:
        return get_runtime_environment_by_env(env=get_factor_env())


class QlibAlphaAgentScenario(QlibFactorScenario):
    """AlphaAgent evolution scenario (mini1-aware prompts when available)."""

    def __init__(self, use_local: bool = True) -> None:
        super().__init__(use_local=use_local)
        train_path = os.environ.get(
            "MINI1_TRAIN_PARQUET",
            "/home/ubuntu/chenyuanhengWorkspace/MAFS5140-Spring2026-Project/mini1/train.parquet",
        )
        qlib_uri = os.environ.get(
            "QLIB_PROVIDER_URI",
            "/home/ubuntu/chenyuanhengWorkspace/QuantaAlpha/data/qlib/mini1_us_5min",
        )
        try:
            self._background = deepcopy(
                T(".prompts:qlib_factor_background").r(
                    runtime_environment=get_runtime_environment_by_env(),
                )
            )
            mini1_note = (
                f"\n\n[MAFS5140 mini1] Factor code runs on 5-minute US panel from train.parquet "
                f"({train_path}). Qlib smoke backtest uses provider {qlib_uri} and "
                f"QA_QLIB_CONF={os.environ.get('QA_QLIB_CONF', 'conf_mini1_smoke50.yaml')}."
            )
            self._background = self._background + mini1_note
        except Exception:
            pass


class QlibFactorFromReportScenario(QlibFactorScenario):
    """Compatibility alias for report-driven factor extraction."""

    pass


__all__ = [
    "FactorExperiment",
    "FactorFBWorkspace",
    "FactorTask",
    "QlibFactorExperiment",
    "QlibFactorScenario",
    "QlibAlphaAgentScenario",
    "QlibFactorFromReportScenario",
    "QlibFBWorkspace",
]
