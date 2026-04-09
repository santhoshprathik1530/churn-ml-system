#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-5001}"

cd "$PROJECT_ROOT"

if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

exec mlflow ui \
  --backend-store-uri "sqlite:///mlflow.db" \
  --default-artifact-root "./mlartifacts" \
  --host "$HOST" \
  --port "$PORT" \
  --allowed-hosts "${HOST}:${PORT},localhost:${PORT},localhost:*" \
  --cors-allowed-origins "http://${HOST}:${PORT},http://localhost:${PORT}"
