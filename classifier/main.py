import json
import sys
from pathlib import Path

from json_uploader import json_uploader
from score import load_weight, classify_emails


def main() -> None:
    base_dir = Path(__file__).parent

    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])

        if not json_path.is_absolute():
            json_path = base_dir / json_path
    else:
        json_path = base_dir / "test.json"

    csv_path = base_dir / "config.csv"
    result_path = base_dir / "result.json"

    emails = json_uploader(json_path)
    weight = load_weight(csv_path)

    results = classify_emails(emails, weight)

    with result_path.open("w", encoding="utf-8") as result_file:
        json.dump(
            results,
            result_file,
            ensure_ascii=False,
            indent=4,
        )

    print(f"Обработано писем: {len(results)}")
    print(f"Результат сохранён в: {result_path}")


if __name__ == "__main__":
    main()