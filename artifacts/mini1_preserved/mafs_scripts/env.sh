#!/usr/bin/env bash
# Source before QuantaAlpha / factor mining (paths + Python; LLM keys in QuantaAlpha/.env).
CHY_WS="${CHY_WS:-/home/ubuntu/chenyuanhengWorkspace}"

export QUANTA_BIN_DIR="${QUANTA_BIN_DIR:-/srv/quant/envs/quantsociety_backend/bin}"
export CONDA_DEFAULT_ENV=quantsociety_backend
export PATH="${QUANTA_BIN_DIR}:${PATH}"

export QUANTA_SHARED_DATA="${QUANTA_SHARED_DATA:-/srv/quant/shared_data/users/chenyuanheng}"
export DATA_RESULTS_DIR="${DATA_RESULTS_DIR:-${QUANTA_SHARED_DATA}/quanta_results}"
export WORKSPACE_PATH="${WORKSPACE_PATH:-${QUANTA_SHARED_DATA}/rdagent_workspace/RD-Agent_workspace}"

export QLIB_DATA_DIR="${QLIB_DATA_DIR:-${CHY_WS}/QuantaAlpha/data/qlib/mini1_us_5min}"
export QLIB_PROVIDER_URI="${QLIB_DATA_DIR}"
export QA_QLIB_CONF="${QA_QLIB_CONF:-conf_mini1_smoke50.yaml}"

export MINI1_TRAIN_PARQUET="${MINI1_TRAIN_PARQUET:-${CHY_WS}/MAFS5140-Spring2026-Project/mini1/train.parquet}"
export FACTOR_CoSTEER_PYTHON_BIN="${QUANTA_BIN_DIR}/python"
export PYTHONPATH="${CHY_WS}/QuantaAlpha:${PYTHONPATH:-}"
export USE_LOCAL=true
export CACHE_WITH_PICKLE="${CACHE_WITH_PICKLE:-false}"

mkdir -p "${WORKSPACE_PATH}" "${DATA_RESULTS_DIR}/results" 2>/dev/null || true
