#!/usr/bin/env bash
set -e

BASE_BASE="/home/leksandro/Projects/Books"

echo "Базова папка: $BASE_BASE"

# перевірка чи існує базова папка
if [ ! -d "$BASE_BASE" ]; then
    echo "❌ Папка $BASE_BASE не існує"
    exit 1
fi

read -rp "Введи назву книги: " BOOK_NAME

if [ -z "$BOOK_NAME" ]; then
    echo "❌ Назва порожня"
    exit 1
fi

SAFE_NAME=$(echo "$BOOK_NAME" | tr ' ' '_' | tr -cd '[:alnum:]_')

PROJECT_DIR="$BASE_BASE/Book_$SAFE_NAME"

echo "👉 Створюю: $PROJECT_DIR"

mkdir -p "$PROJECT_DIR"/{data/{original,chunks,processed},prompts,flows,state,output/scenes}

touch "$PROJECT_DIR/data/processed/bible.json"
touch "$PROJECT_DIR/data/processed/skeleton.json"

touch "$PROJECT_DIR/prompts/bible.txt"
touch "$PROJECT_DIR/prompts/skeleton.txt"
touch "$PROJECT_DIR/prompts/writer.txt"
touch "$PROJECT_DIR/prompts/editor.txt"
touch "$PROJECT_DIR/prompts/censor.txt"

touch "$PROJECT_DIR/flows/build_bible.py"
touch "$PROJECT_DIR/flows/build_skeleton.py"
touch "$PROJECT_DIR/flows/write_book.py"

touch "$PROJECT_DIR/state/memory.json"
touch "$PROJECT_DIR/state/characters.json"

touch "$PROJECT_DIR/output/final.txt"

touch "$PROJECT_DIR/main.py"

echo "✅ Готово"
ls -R "$PROJECT_DIR"
