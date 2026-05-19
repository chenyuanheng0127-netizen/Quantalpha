#!/usr/bin/env bash
# Print monitoring hints at top of mine log.
LOG="${1:?log path}"
PID="${2:-}"
{
  echo ""
  echo "===== MINI1 MINE 监控（$(date -Iseconds)）====="
  echo "日志文件: ${LOG}"
  echo "实验 ID:  ${EXPERIMENT_ID:-unknown}"
  echo "PID 文件: /tmp/quantaalpha_mine.pid"
  [[ -n "$PID" ]] && echo "当前 PID: $PID"
  echo ""
  echo "grep -E 'Task done|Running task|Execute factor' '${LOG}' | tail -10"
  echo "===== 以上为监控命令，mine 输出从下一行开始 ====="
  echo ""
} >>"$LOG"
