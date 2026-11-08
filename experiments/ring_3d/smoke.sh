#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPOSITORY_ROOT=$(realpath "$SCRIPT_DIR/../..")
SPRAY_OUTPUT="$REPOSITORY_ROOT/runs/ring_3d/spray_copies_16"

uv --project "$REPOSITORY_ROOT" run --locked python "$SCRIPT_DIR/run.py" \
  --profile "$SCRIPT_DIR/profiles/smoke_8.json" \
  --output "$REPOSITORY_ROOT/runs/ring_3d/smoke_8" \
  --clean

# A sprayed fabric with one lossy downlink, on which the hold selector sends
# exploration copies; flow_events.csv must count every one of them.
uv --project "$REPOSITORY_ROOT" run --locked python "$SCRIPT_DIR/run.py" \
  --profile "$SCRIPT_DIR/profiles/spray_copies_16.json" \
  --output "$SPRAY_OUTPUT" --clean

uv --project "$REPOSITORY_ROOT" run --locked python \
  "$SCRIPT_DIR/check_exploration_copies.py" "$SPRAY_OUTPUT"
