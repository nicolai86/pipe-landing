#!/usr/bin/env bash
# Stamp the RotaryCAM version into pipe-landing/version.js (read from the main
# repo's latest tag, or $ROTARYCAM_VERSION). Run at release time after tagging.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/version.py --write-js version.js
