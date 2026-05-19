#!/usr/bin/env bash
# Resume mini1_more evolution (uses evolution_state.json + QUANTA_LOG_RESUME_DIR).
set -euo pipefail

MAFS="/home/ubuntu/chenyuanhengWorkspace/MAFS5140-Spring2026-Project"
QA="/home/ubuntu/chenyuanhengWorkspace/QuantaAlpha"
QUANTA="/srv/quant/envs/quantsociety_backend/bin/quantaalpha"
RESUME_LOG="${QUANTA_LOG_RESUME_DIR:-$QA/log/2026-05-18_08-39-31-349821}"

bash "$MAFS/scripts/kill_mine.sh" || true
sleep 2

source "$MAFS/scripts/env.sh"
if [[ ! -f "$QA/.env" ]]; then
  echo "ERROR: missing $QA/.env (LLM API keys). Restore from backup or cp configs/.env.example .env"
  exit 1
fi
set -a && source "$QA/.env" && set +a

export PYTHONPATH="$QA:${PYTHONPATH:-}"
export CONFIG_PATH="${CONFIG_PATH:-configs/experiment_stage5_more_resume.yaml}"
export EXPERIMENT_ID="mini1_more_20260518"
export QUANTA_LOG_RESUME_DIR="$RESUME_LOG"
export PICKLE_CACHE_FOLDER_PATH_STR="${PICKLE_CACHE_FOLDER_PATH_STR:-${DATA_RESULTS_DIR}/pickle_cache_${EXPERIMENT_ID}}"
export QA_MERGED_POOL_CONTEXT_PATH=""
mkdir -p "$WORKSPACE_PATH" "$PICKLE_CACHE_FOLDER_PATH_STR" "$RESUME_LOG"

NCPU=$(nproc)
HALF=$((NCPU / 2))
[[ "$HALF" -lt 1 ]] && HALF=1
CPU_LIST="0-$((HALF - 1))"
export OMP_NUM_THREADS="$HALF"
export MKL_NUM_THREADS="$HALF"
export OPENBLAS_NUM_THREADS="$HALF"
export NUMEXPR_MAX_THREADS="$HALF"
export VECLIB_MAXIMUM_THREADS="$HALF"

MINE_LOG="$MAFS/mini1_results/logs/mine_rerun_mini1_more_20260518.log"
echo "" >> "$MINE_LOG"
echo "===== STAGE5 RESUME $(date -Is) CPU cores=${CPU_LIST} threads=${HALF} log=${RESUME_LOG} =====" >> "$MINE_LOG"
bash "$MAFS/scripts/mine_log_banner.sh" "$MINE_LOG"

cd "$QA"
nohup env CONFIG_PATH="$CONFIG_PATH" EXPERIMENT_ID="$EXPERIMENT_ID" \
  QUANTA_LOG_RESUME_DIR="$QUANTA_LOG_RESUME_DIR" \
  WORKSPACE_PATH="$WORKSPACE_PATH" \
  DATA_RESULTS_DIR="$DATA_RESULTS_DIR" \
  PICKLE_CACHE_FOLDER_PATH_STR="$PICKLE_CACHE_FOLDER_PATH_STR" \
  QA_QLIB_CONF="$QA_QLIB_CONF" \
  MINI1_TRAIN_PARQUET="$MINI1_TRAIN_PARQUET" \
  QLIB_DATA_DIR="$QLIB_DATA_DIR" QLIB_PROVIDER_URI="$QLIB_PROVIDER_URI" \
  QA_MERGED_POOL_CONTEXT_PATH="" CACHE_WITH_PICKLE=false USE_LOCAL=true \
  OMP_NUM_THREADS="$OMP_NUM_THREADS" MKL_NUM_THREADS="$MKL_NUM_THREADS" \
  OPENBLAS_NUM_THREADS="$OPENBLAS_NUM_THREADS" NUMEXPR_MAX_THREADS="$NUMEXPR_MAX_THREADS" \
  PYTHONPATH="$PYTHONPATH" \
  taskset -c "$CPU_LIST" nice -n 10 \
  "$QUANTA" mine \
  --direction "US 5min price-volume alpha on mini1 train data" \
  --config_path "$CONFIG_PATH" \
  >> "$MINE_LOG" 2>&1 &

echo $! > /tmp/quantaalpha_mine.pid
bash "$MAFS/scripts/mine_log_banner.sh" "$MINE_LOG" "$(cat /tmp/quantaalpha_mine.pid)"
echo "mine PID=$(cat /tmp/quantaalpha_mine.pid) log=$MINE_LOG"
