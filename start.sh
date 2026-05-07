#!/usr/bin/env bash
set -euo pipefail

# ============================================================
#  start.sh — запуск Book Pipeline з логуванням
# ============================================================

BASE_DIR="/home/leksandro/Projects/Books"
VENV_DIR="$BASE_DIR/venv"
LOG_DIR="$BASE_DIR/logs"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/run_$TIMESTAMP.log"

mkdir -p "$LOG_DIR"

echo "======================================"
echo "Запуск Book Pipeline"
echo "Час: $TIMESTAMP"
echo "Лог: $LOG_FILE"
echo "======================================"

# ── 1. Перевірка venv ───────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ venv не знайдено: $VENV_DIR"
    exit 1
fi

# ── 2. Активація ────────────────────────────────────────────
source "$VENV_DIR/bin/activate"

echo "✔ Python: $(python --version)"

# ── 3. Перевірка Ollama ─────────────────────────────────────
if ! command -v ollama &>/dev/null; then
    echo "❌ Ollama не знайдено"
    exit 1
fi

echo "✔ Ollama: $(ollama --version)"

# ── 4. Перевірка чи запущений Ollama ────────────────────────
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠ Ollama не запущений, пробую стартувати..."
    nohup ollama serve > "$LOG_DIR/ollama_$TIMESTAMP.log" 2>&1 &
    sleep 2
fi

# ── 5. Перевірка моделі ─────────────────────────────────────
MODEL="writer:latest"

if ! ollama list | grep -q "$MODEL"; then
    echo "❌ Модель $MODEL не знайдена"
    exit 1
fi

echo "✔ Модель: $MODEL"

# ── 6. Запуск main.py з логуванням ──────────────────────────
echo ""
echo "=== Запуск main.py ==="
echo ""

python "$BASE_DIR/main.py" 2>&1 | tee "$LOG_FILE"

echo ""
echo "======================================"
echo "✅ Завершено"
echo "Лог збережено: $LOG_FILE"
echo "======================================"
