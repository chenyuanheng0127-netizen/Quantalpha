#!/usr/bin/env bash
# Clean original pass: rebuild D0-D3 original trajectories before enabling mutation.
set -euo pipefail

CHY_WS="${CHY_WS:-/home/ubuntu/chenyuanhengWorkspace}"
MAFS="$CHY_WS/MAFS5140-Spring2026-Project"
QA="$CHY_WS/QuantaAlpha"
QUANTA="/srv/quant/envs/quantsociety_backend/bin/quantaalpha"

bash "$MAFS/scripts/kill_mine.sh" || true
sleep 2

source "$MAFS/scripts/env.sh"
if [[ ! -f "$QA/.env" ]]; then
  echo "ERROR: missing $QA/.env"
  exit 1
fi
set -a && source "$QA/.env" && set +a

export PYTHONPATH="$QA:${PYTHONPATH:-}"
export CONFIG_PATH="configs/experiment_stage5_original_clean.yaml"
export EXPERIMENT_ID="mini1_original_clean_20260519"
export QA_DISABLE_COSTEER_RAG=true
export CHAT_MODEL="${CHAT_MODEL_OVERRIDE:-deepseek-v3.2}"
export REASONING_MODEL="${REASONING_MODEL_OVERRIDE:-deepseek-v3.2}"
unset QUANTA_LOG_RESUME_DIR
export PICKLE_CACHE_FOLDER_PATH_STR="${DATA_RESULTS_DIR}/pickle_cache_${EXPERIMENT_ID}"
export QA_MERGED_POOL_CONTEXT_PATH=""
mkdir -p "$WORKSPACE_PATH" "$PICKLE_CACHE_FOLDER_PATH_STR" "$MAFS/mini1_results/logs"

export OMP_NUM_THREADS=6
export MKL_NUM_THREADS=6
export OPENBLAS_NUM_THREADS=6
export NUMEXPR_MAX_THREADS=6
export VECLIB_MAXIMUM_THREADS=6
export MULTI_PROC_N=1

MINE_LOG="$MAFS/mini1_results/logs/mine_original_clean_20260519.log"
echo "" >> "$MINE_LOG"
echo "===== ORIGINAL CLEAN $(date -Is) 6 cores config=$CONFIG_PATH =====" >> "$MINE_LOG"
bash "$MAFS/scripts/mine_log_banner.sh" "$MINE_LOG"

cd "$QA"
nohup env CONFIG_PATH="$CONFIG_PATH" EXPERIMENT_ID="$EXPERIMENT_ID" \
  CONDA_DEFAULT_ENV="${CONDA_DEFAULT_ENV:-quantsociety_backend}" \
  WORKSPACE_PATH="$WORKSPACE_PATH" DATA_RESULTS_DIR="$DATA_RESULTS_DIR" \
  PICKLE_CACHE_FOLDER_PATH_STR="$PICKLE_CACHE_FOLDER_PATH_STR" \
  QA_QLIB_CONF="$QA_QLIB_CONF" MINI1_TRAIN_PARQUET="$MINI1_TRAIN_PARQUET" \
  QLIB_DATA_DIR="$QLIB_DATA_DIR" QLIB_PROVIDER_URI="$QLIB_PROVIDER_URI" \
  QA_MERGED_POOL_CONTEXT_PATH="" CACHE_WITH_PICKLE=false USE_LOCAL=true \
  QA_DISABLE_COSTEER_RAG="$QA_DISABLE_COSTEER_RAG" \
  CHAT_MODEL="$CHAT_MODEL" REASONING_MODEL="$REASONING_MODEL" \
  MULTI_PROC_N="$MULTI_PROC_N" \
  OMP_NUM_THREADS="$OMP_NUM_THREADS" MKL_NUM_THREADS="$MKL_NUM_THREADS" \
  OPENBLAS_NUM_THREADS="$OPENBLAS_NUM_THREADS" NUMEXPR_MAX_THREADS="$NUMEXPR_MAX_THREADS" \
  PYTHONPATH="$PYTHONPATH" \
  nice -n 5 taskset -c 2-7 \
  "$QUANTA" mine \
  --direction "US 5min price-volume alpha on mini1 train data" \
  --config_path "$CONFIG_PATH" \
  >> "$MINE_LOG" 2>&1 &

echo $! > /tmp/quantaalpha_mine.pid
bash "$MAFS/scripts/mine_log_banner.sh" "$MINE_LOG" "$(cat /tmp/quantaalpha_mine.pid)"
echo "mine PID=$(cat /tmp/quantaalpha_mine.pid) log=$MINE_LOG"
