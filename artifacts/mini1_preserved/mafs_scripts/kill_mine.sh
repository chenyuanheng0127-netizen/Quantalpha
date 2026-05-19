#!/usr/bin/env bash
set -euo pipefail
if [[ -f /tmp/quantaalpha_mine.pid ]]; then
  pid=$(cat /tmp/quantaalpha_mine.pid 2>/dev/null || true)
  if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    sleep 2
    kill -9 "$pid" 2>/dev/null || true
    echo "Stopped mine PID $pid"
  fi
fi
pkill -f 'quantaalpha mine' 2>/dev/null || true
