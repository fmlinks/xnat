#!/usr/bin/env bash
set -euo pipefail

# One-click runner for Linux/WSL/macOS.
# - Creates a local venv (.venv) if missing
# - Installs requirements
# - Runs uploader (defaults to config/config.yaml)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "[INFO] Creating venv..."
  python3 -m venv .venv
  echo "[INFO] Installing dependencies..."
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
fi

.venv/bin/python run.py "$@"
