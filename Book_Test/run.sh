#!/usr/bin/env bash
# run.sh — запуск Book Pipeline через venv
set -euo pipefail

VENV_DIR="/home/leksandro/Projects/Books/venv"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "❌ venv не знайдено: $VENV_DIR"
    echo "   Спочатку запусти install.sh"
    exit 1
fi

source "$VENV_DIR/bin/activate"

# Запускаємо з папки де лежить run.sh (папка книги)
cd "$(dirname "$0")"

python main.py "$@"
