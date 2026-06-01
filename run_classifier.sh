#!/bin/bash

set -e

if [ "$#" -ne 3 ]; then
    echo "Использование: ./run_classifier.sh parsed_json input_folder output_folder"
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
JSON_FILE="$1"
INPUT_FOLDER="$2"
OUTPUT_FOLDER="$3"
LOG_FOLDER="$PROJECT_DIR/logs"
LOG_FILE="$LOG_FOLDER/classifier.log"

if [ ! -f "$JSON_FILE" ]; then
    echo "JSON-файл не найден: $JSON_FILE"
    exit 1
fi

if [ ! -d "$INPUT_FOLDER" ]; then
    echo "Папка с письмами не найдена: $INPUT_FOLDER"
    exit 1
fi

mkdir -p "$OUTPUT_FOLDER"
mkdir -p "$LOG_FOLDER"

echo "Старт классификации: $(date)" | tee "$LOG_FILE"
echo "JSON: $JSON_FILE" | tee -a "$LOG_FILE"
echo "Папка писем: $INPUT_FOLDER" | tee -a "$LOG_FILE"
echo "Папка результата: $OUTPUT_FOLDER" | tee -a "$LOG_FILE"

python3 "$PROJECT_DIR/classifier/main.py" \
    "$JSON_FILE" \
    "$INPUT_FOLDER" \
    "$OUTPUT_FOLDER" 2>&1 | tee -a "$LOG_FILE"

echo "Готово: $(date)" | tee -a "$LOG_FILE"
echo "Лог сохранён в: $LOG_FILE"
