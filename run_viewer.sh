#!/bin/bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

if command -v python3 >/dev/null 2>&1 && python3 --version >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1 && python --version >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "Python не найден"
    exit 1
fi

if [ "$#" -eq 0 ]; then
    RESULT_FILE="$PROJECT_DIR/classifier/result.json"
elif [ "$#" -eq 1 ]; then
    RESULT_FILE="$1"
else
    echo "Использование: ./run_viewer.sh [result_json]"
    exit 1
fi

if [ ! -f "$RESULT_FILE" ]; then
    echo "Файл результата не найден: $RESULT_FILE"
    exit 1
fi

"$PYTHON_BIN" "$PROJECT_DIR/result_viewer.py" "$RESULT_FILE"
