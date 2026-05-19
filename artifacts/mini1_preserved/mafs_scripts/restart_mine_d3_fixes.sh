#!/usr/bin/env bash
# Restart D3 only: evolution_state directions_completed=[0,1,2], 6 cores, all mini1 fixes.
set -euo pipefail

MAFS="/home/ubuntu/chenyuanhengWorkspace/MAFS5140-Spring2026-Project"
QA="/home/ubuntu/chenyuanhengWorkspace/QuantaAlpha"
QUANTA="/srv/quant/envs/quantsociety_backend/bin/quantaalpha"
RESUME_LOG="${QUANTA_LOG_RESUME_DIR:-$QA/log/2026-05-18_08-39-31-349821}"

bash "$MAFS/scripts/kill_mine.sh" || true
sleep 2
rm -rf "$RESUME_LOG/original_00_03"

source "$MAFS/scripts/env.sh"
if [[ ! -f "$QA/.env" ]]; then
  echo "ERROR: missing $QA/.env — 之前能跑是因为 restart 脚本里 source 了这个文件。"
  echo "请恢复: cp $QA/configs/.env.example $QA/.env 并填入 OPENAI_API_KEY / OPENAI_BASE_URL"
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

# 6 cores (reserve 0-1 for others)
export OMP_NUM_THREADS=6
export MKL_NUM_THREADS=6
export OPENBLAS_NUM_THREADS=6
export NUMEXPR_MAX_THREADS=6
export VECLIB_MAXIMUM_THREADS=6
export MULTI_PROC_N=1

MINE_LOG="$MAFS/mini1_results/logs/mine_rerun_mini1_more_20260518.log"
echo "" >> "$MINE_LOG"
echo "===== D3 RESTART $(date -Is) 6 cores OMP=6 resume=$RESUME_LOG =====" >> "$MINE_LOG"
bash "$MAFS/scripts/mine_log_banner.sh" "$MINE_LOG"

cd "$QA"
nohup env CONFIG_PATH="$CONFIG_PATH" EXPERIMENT_ID="$EXPERIMENT_ID" \
  CONDA_DEFAULT_ENV="${CONDA_DEFAULT_ENV:-quantsociety_backend}" \
  QUANTA_LOG_RESUME_DIR="$QUANTA_LOG_RESUME_DIR" \
  WORKSPACE_PATH="$WORKSPACE_PATH" DATA_RESULTS_DIR="$DATA_RESULTS_DIR" \
  PICKLE_CACHE_FOLDER_PATH_STR="$PICKLE_CACHE_FOLDER_PATH_STR" \
  QA_QLIB_CONF="$QA_QLIB_CONF" MINI1_TRAIN_PARQUET="$MINI1_TRAIN_PARQUET" \
  QLIB_DATA_DIR="$QLIB_DATA_DIR" QLIB_PROVIDER_URI="$QLIB_PROVIDER_URI" \
  QA_MERGED_POOL_CONTEXT_PATH="" CACHE_WITH_PICKLE=false USE_LOCAL=true \
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
