#!/usr/bin/env bash
# Run the full pytest suite and generate the execution report.
# Usage: ./scripts/run_tests.sh [extra pytest args, e.g. -m smoke]
set -u
cd "$(dirname "$0")/.."
python -m pytest "$@"
status=$?
python scripts/generate_report.py
exit $status
