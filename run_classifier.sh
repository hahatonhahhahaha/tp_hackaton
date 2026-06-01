#!/bin/bash

set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "Использование: ./run_classifier.sh input_folder output_folder"
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT_FOLDER="$1"
OUTPUT_FOLDER="$2"
LOG_FOLDER="$PROJECT_DIR/logs"
LOG_FILE="$LOG_FOLDER/classifier.log"
JSON_FILE="$OUTPUT_FOLDER/all_mails.json"
RESULT_FILE="$OUTPUT_FOLDER/result.json"

if [ ! -d "$INPUT_FOLDER" ]; then
    echo "Папка с письмами не найдена: $INPUT_FOLDER"
    exit 1
fi

if command -v python3 >/dev/null 2>&1 && python3 --version >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1 && python --version >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "Python не найден"
    exit 1
fi

mkdir -p "$OUTPUT_FOLDER"
mkdir -p "$LOG_FOLDER"

echo "Старт: $(date)" | tee "$LOG_FILE"
echo "Папка писем: $INPUT_FOLDER" | tee -a "$LOG_FILE"
echo "Папка результата: $OUTPUT_FOLDER" | tee -a "$LOG_FILE"

"$PYTHON_BIN" "$PROJECT_DIR/app/app.py" \
    "$INPUT_FOLDER" \
    "$JSON_FILE" 2>&1 | tee -a "$LOG_FILE"

"$PYTHON_BIN" "$PROJECT_DIR/classifier/main.py" \
    "$JSON_FILE" \
    "$INPUT_FOLDER" \
    "$OUTPUT_FOLDER" \
    "$RESULT_FILE" 2>&1 | tee -a "$LOG_FILE"

echo "Готово: $(date)" | tee -a "$LOG_FILE"
echo "Лог сохранён: $LOG_FILE"
