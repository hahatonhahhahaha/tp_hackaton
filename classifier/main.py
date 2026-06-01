import json
import shutil
import sys
from pathlib import Path

from json_uploader import json_uploader
from score import classify_emails, load_weight


def make_unique_path(file_path: Path) -> Path:
    if not file_path.exists():
        return file_path

    counter = 1

    while True:
        new_name = f"{file_path.stem}_{counter}{file_path.suffix}"
        new_path = file_path.with_name(new_name)

        if not new_path.exists():
            return new_path

        counter += 1


def move_email_files(
    results: list[dict],
    input_folder: Path,
    output_folder: Path,
) -> None:
    if not input_folder.exists():
        raise FileNotFoundError(f"Папка не найдена: {input_folder}")

    if not input_folder.is_dir():
        raise NotADirectoryError(f"Это не папка: {input_folder}")

    output_folder.mkdir(parents=True, exist_ok=True)

    for result in results:
        file_name = str(result.get("file_name") or "").strip()

        if not file_name:
            result["move_status"] = "пропущено: нет имени файла"
            continue

        mail_file = input_folder / Path(file_name).name

        if not mail_file.exists():
            result["move_status"] = "пропущено: файл не найден"
            continue

        category_folder = output_folder / result["category"]
        category_folder.mkdir(parents=True, exist_ok=True)

        new_file = make_unique_path(category_folder / mail_file.name)
        shutil.move(str(mail_file), str(new_file))

        result["move_status"] = "перемещено"
        result["moved_to"] = str(new_file)


def save_results(results: list[dict], result_path: Path) -> None:
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )


def resolve_path(path: str, base_dir: Path) -> Path:
    result = Path(path)
    if result.is_absolute():
        return result
    if result.exists():
        return result
    return base_dir / result


def run_classifier(
    json_path: Path,
    input_folder: Path | None,
    output_folder: Path | None,
    result_path: Path,
) -> list[dict]:
    base_dir = Path(__file__).parent
    csv_path = base_dir / "config.csv"
    emails = json_uploader(json_path)
    weight = load_weight(csv_path)
    results = classify_emails(emails, weight)

    if input_folder is not None and output_folder is not None:
        move_email_files(results, input_folder, output_folder)

    save_results(results, result_path)
    return results


def main() -> int:
    base_dir = Path(__file__).parent

    if len(sys.argv) not in (1, 2, 4, 5):
        print(
            "Использование: python classifier/main.py "
            "json_path input_folder output_folder result_json"
        )
        return 1

    json_path = base_dir / "test.json"
    result_path = base_dir / "result.json"
    input_folder = None
    output_folder = None

    if len(sys.argv) >= 2:
        json_path = resolve_path(sys.argv[1], base_dir)

    if len(sys.argv) >= 4:
        input_folder = resolve_path(sys.argv[2], Path.cwd())
        output_folder = resolve_path(sys.argv[3], Path.cwd())
        result_path = output_folder / "result.json"

    if len(sys.argv) == 5:
        result_path = resolve_path(sys.argv[4], Path.cwd())

    results = run_classifier(json_path, input_folder, output_folder, result_path)

    moved_count = sum(
        1 for result in results if result.get("move_status") == "перемещено"
    )
    skipped_count = sum(
        1
        for result in results
        if str(result.get("move_status", "")).startswith("пропущено")
    )

    print(f"Обработано писем: {len(results)}")
    print(f"Перемещено файлов: {moved_count}")
    print(f"Пропущено файлов: {skipped_count}")
    print(f"Результат сохранён: {result_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
