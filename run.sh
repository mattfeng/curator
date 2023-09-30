#!/bin/bash

set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

echo "run.sh is found in ${SCRIPT_DIR}"

python "${SCRIPT_DIR}/fetch_recent_papers.py"
python "${SCRIPT_DIR}/curate.py"