#!/usr/bin/env bash
# Start the bundled mock LMS, run the Postman collection with Newman, then stop the app.
# Requires: Node.js and Newman (npm install -g newman).
# To test a real LMS instead, run:  newman run postman/LMS_API.postman_collection.json -e <your-env>.json
set -u
cd "$(dirname "$0")/.."
mkdir -p reports
python -m app.lms_app > reports/mock_lms.log 2>&1 &
APP_PID=$!
trap 'kill $APP_PID 2>/dev/null' EXIT
for _ in $(seq 1 30); do
  curl -sf http://127.0.0.1:5000/api/health >/dev/null && break
  sleep 0.5
done
newman run postman/LMS_API.postman_collection.json \
  -e postman/LMS_Local.postman_environment.json \
  -r cli,junit,html --reporter-junit-export reports/newman-junit.xml \
  --reporter-html-export reports/newman-report.html
