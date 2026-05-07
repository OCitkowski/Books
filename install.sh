#!/usr/bin/env bash
set -euo pipefail

# ============================================================
#  Install.sh — Book Pipeline (з фіксованим Python)
# ============================================================

BASE_DIR="/home/leksandro/Projects/Books"
VENV_DIR="$BASE_DIR/venv"
PYTHON_VERSION="3.11"

echo "=== Setup Book Pipeline ==="

# ── 1. uv (обов’язково) ─────────────────────────────────────
if ! command -v uv &>/dev/null; then
    echo "Встановлюю uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✔ uv: $(uv --version)"

# ── 2. Створення venv з НОРМАЛЬНИМ Python ───────────────────
mkdir -p "$BASE_DIR"

if [[ -d "$VENV_DIR" ]]; then
    echo "⚠ venv вже існує"
else
    echo "Створюю venv з Python $PYTHON_VERSION"
    uv venv "$VENV_DIR" --python "$PYTHON_VERSION"
fi

# ── 3. Активація ────────────────────────────────────────────
source "$VENV_DIR/bin/activate"

echo "✔ Python у venv:"
python --version

# ── 4. pip ─────────────────────────────────────────────────
uv pip install --upgrade pip setuptools wheel

# ── 5. Залежності (перевірені сумісні) ──────────────────────
echo "Встановлюю залежності..."

uv pip install \
    langchain==0.2.6 \
    langchain-community==0.2.6 \
    langchain-ollama==0.1.0 \
    langgraph==0.1.5 \
    ollama==0.3.3 \
    tiktoken \
    python-dotenv

# ── 6. Перевірка ───────────────────────────────────────────
python - <<EOF
import langchain
import langgraph
import ollama
import sys
print("OK:", sys.version)
EOF

# ── 7. Ollama CLI ──────────────────────────────────────────
if ! command -v ollama &>/dev/null; then
    echo "⚠ Ollama не знайдено (постав окремо)"
else
    echo "✔ Ollama: $(ollama --version)"
fi

# ── 8. Скрипт запуску ──────────────────────────────────────
START_SCRIPT="$BASE_DIR/start_env.sh"

cat > "$START_SCRIPT" <<START
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
cd "$BASE_DIR"
echo "Python:"
python --version
exec "\$SHELL"
START

chmod +x "$START_SCRIPT"

# ── Фініш ─────────────────────────────────────────────────
echo ""
echo "======================================"
echo "✅ Готово (Python зафіксований)"
echo "======================================"
echo ""
echo "Запуск:"
echo "  source $VENV_DIR/bin/activate"
echo "або:"
echo "  $START_SCRIPT"
echo ""
