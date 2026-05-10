#!/bin/bash
# Helper to trigger a Jenkins build for the heart-disease-mlops job from the host.
# Uses a single curl session so the CSRF crumb stays valid (Jenkins binds the
# crumb to JSESSIONID).
set -e
JAR=/tmp/jenkins.cookies
URL=http://127.0.0.1:8081
USER=admin:admin
JOB=heart-disease-mlops
rm -f "$JAR"
CRUMB=$(curl -s -u "$USER" -c "$JAR" "$URL/crumbIssuer/api/json" | python3 -c "import json,sys;print(json.load(sys.stdin)['crumb'])")
echo "crumb=${CRUMB:0:16}..."
HTTP=$(curl -s -o /tmp/build.out -w "%{http_code}" -u "$USER" -b "$JAR" -c "$JAR" -H "Jenkins-Crumb: $CRUMB" -X POST "$URL/job/$JOB/build")
echo "POST /build -> HTTP $HTTP"
sleep 2
NUMS=$(curl -s -u "$USER" "$URL/job/$JOB/api/json" | python3 -c "import json,sys;d=json.load(sys.stdin);print('next:',d.get('nextBuildNumber'),'last:',d.get('lastBuild',{}).get('number'))")
echo "$NUMS"
