#!/bin/sh
# Sets up a fresh machine or container for the pipeline. Safe to re-run.
#
#   sh setup.sh
#
# Needs: python3 (3.12 tested), node 22.18 or newer, ffmpeg with ffprobe
# and the rubberband filter. Writes .venv/ and studio/node_modules/, both
# gitignored, and downloads Remotion's headless browser into
# studio/node_modules/.remotion/. There is no GPU in most cloud
# containers: every render passes --gl=swangle.
set -e
cd "$(dirname "$0")"

command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg is missing"; exit 1; }
ffmpeg -hide_banner -filters 2>/dev/null | grep -q rubberband || echo "warning: this ffmpeg has no rubberband filter; mix.py needs it only to slow a slightly short music bed"

if command -v uv >/dev/null 2>&1; then
  [ -x .venv/bin/python ] || uv venv -q -p 3.12 .venv
  VIRTUAL_ENV="$PWD/.venv" uv pip install -q -r requirements.txt
else
  [ -x .venv/bin/python ] || python3 -m venv .venv
  .venv/bin/python -m pip install -q -r requirements.txt
fi

(cd studio && npm ci --no-audit --no-fund --loglevel=error && npx remotion browser ensure >/dev/null)
[ -f .env ] || cp .env.example .env
echo "set up: .venv (pipeline), studio/node_modules (Remotion and its browser), .env (fill in the key)"
