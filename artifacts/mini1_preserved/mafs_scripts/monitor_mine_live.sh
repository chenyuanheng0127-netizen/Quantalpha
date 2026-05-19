#!/usr/bin/env bash
# Live dashboard for QuantaAlpha mini1 mining.
set -euo pipefail

CHY_WS="${CHY_WS:-/home/ubuntu/chenyuanhengWorkspace}"
MAFS="$CHY_WS/MAFS5140-Spring2026-Project"
DEFAULT_LOG="$MAFS/mini1_results/logs/mine_original_clean_20260519.log"
LOG="${1:-$DEFAULT_LOG}"
INTERVAL="${INTERVAL:-5}"
PID_FILE="${PID_FILE:-/tmp/quantaalpha_mine.pid}"
WORKSPACE_ROOT="${WORKSPACE_PATH:-/srv/quant/shared_data/users/chenyuanheng/rdagent_workspace/RD-Agent_workspace}"
SHARED_ROOT="/srv/quant/shared_data/users/chenyuanheng"

if [[ ! -f "$LOG" ]]; then
  echo "Log file not found: $LOG"
  exit 1
fi

while true; do
  clear 2>/dev/null || true
  now="$(date -Is)"
  pid=""
  [[ -f "$PID_FILE" ]] && pid="$(cat "$PID_FILE" 2>/dev/null || true)"

  echo "===== QuantaAlpha Mini1 Live Monitor ====="
  echo "time: $now"
  echo "log : $LOG"
  echo "pid : ${pid:-unknown}"
  echo ""

  echo "----- Process -----"
  if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
    ps -p "$pid" -o pid,ppid,stat,pcpu,pmem,rss,etime,cmd
  else
    echo "mine process is not running"
  fi
  echo ""

  echo "----- Factor Child Processes -----"
  pgrep -af 'python .*factor.py' || echo "no factor.py child process"
  echo ""

  echo "----- Memory / Disk -----"
  free -h | sed -n '1,3p'
  df -h "$SHARED_ROOT" /home/ubuntu/chenyuanhengWorkspace 2>/dev/null || true
  echo ""

  echo "----- Recent Progress -----"
  grep -E 'Generated [0-9]+ exploration directions|Running task|factor_propose took|factor_construct took|factor_calculate took|Start factor backtest|Execute factor backtest|Saved combined factors|Backtesting results|Task done|Evolution complete' "$LOG" | tail -18 || true
  echo ""

  echo "----- Recent Errors / Warnings -----"
  grep -E 'ERROR|Traceback|Task failed|AttributeError|FileNotFoundError|Killed|No result file|Backtesting result is None|failed to run command|daily_pv\.h5|return_checking' "$LOG" | tail -14 || true
  echo ""

  echo "----- Current Factor Workspaces -----"
  grep -Eo '/srv/quant/shared_data/users/chenyuanheng/rdagent_workspace/RD-Agent_workspace/[a-f0-9]+' "$LOG" \
    | tail -6 \
    | while read -r d; do
        [[ -d "$d" ]] || continue
        size="$(du -sh "$d" 2>/dev/null | awk '{print $1}')"
        h5="$(ls -lh "$d"/result.h5 2>/dev/null | awk '{print $5}' || true)"
        echo "$size  result.h5=${h5:-missing}  $d"
      done
  echo ""

  echo "----- Log Tail -----"
  tail -20 "$LOG"
  echo ""
  echo "Refresh interval: ${INTERVAL}s. Press Ctrl-C to stop."
  sleep "$INTERVAL"
done
