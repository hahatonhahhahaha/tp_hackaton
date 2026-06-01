import json
import shutil
import sys
from pathlib import Path

from json_uploader import json_uploader
from score import load_weight, classify_emails


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
        print(f"Папка не найдена: {input_folder}")
        return

    if not input_folder.is_dir():
        print(f"Это не папка: {input_folder}")
        return

    output_folder.mkdir(parents=True, exist_ok=True)

    moved_count = 0
    skipped_count = 0

    for result in results:
        file_name = str(result.get("file_name") or "").strip()

        if not file_name:
            result["move_status"] = "пропущено: нет имени файла"
            skipped_count += 1
            continue

        mail_file = input_folder / Path(file_name).name

        if not mail_file.exists():
            result["move_status"] = "пропущено: файл не найден"
            skipped_count += 1
            continue

        category_folder = output_folder / result["category"]
        category_folder.mkdir(parents=True, exist_ok=True)

        new_file = make_unique_path(category_folder / mail_file.name)
        shutil.move(str(mail_file), str(new_file))

        result["move_status"] = "перемещено"
        result["moved_to"] = str(new_file)
        moved_count += 1

    print(f"Перемещено файлов: {moved_count}")
    print(f"Пропущено файлов: {skipped_count}")


def main() -> None:
    base_dir = Path(__file__).parent
    csv_path = base_dir / "config.csv"
    result_path = base_dir / "result.json"

    json_path = base_dir / "test.json"

    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])

        if not json_path.is_absolute() and not json_path.exists():
            json_path = base_dir / json_path

    emails = json_uploader(json_path)
    weight = load_weight(csv_path)

    results = classify_emails(emails, weight)

    if len(sys.argv) > 3:
        input_folder = Path(sys.argv[2])
        output_folder = Path(sys.argv[3])

        if not input_folder.is_absolute():
            input_folder = Path.cwd() / input_folder

        if not output_folder.is_absolute():
            output_folder = Path.cwd() / output_folder

        move_email_files(
            results=results,
            input_folder=input_folder,
            output_folder=output_folder,
        )
    elif len(sys.argv) == 3:
        print("Для перемещения нужно указать входную и выходную папку")

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
