#!/bin/bash
# Poll a Jenkins build until it completes; print result + duration.
# Usage:  bash ci_cd/poll_build.sh [build_number] [job_name]
set -e
N=${1:-2}
JOB=${2:-heart-disease-mlops}
USER=admin:admin
URL=http://127.0.0.1:8081
for i in $(seq 1 90); do
  J=$(curl -s -u "$USER" "$URL/job/$JOB/$N/api/json" 2>/dev/null || echo '{}')
  STATE=$(echo "$J" | python3 -c "import json,sys
try: d=json.loads(sys.stdin.read())
except: d={}
print(d.get('result'),'|building=',d.get('building'),'|dur=',d.get('duration'))" 2>/dev/null)
  echo "[$(date +%H:%M:%S)] $STATE"
  case "$STATE" in
    SUCCESS*|FAILURE*|ABORTED*|UNSTABLE*) break ;;
  esac
  sleep 15
done
