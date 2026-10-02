#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
uv run --locked --no-sync alembic upgrade head