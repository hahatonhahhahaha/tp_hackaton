import json
import sys
from pathlib import Path

try:
    from .mail_parser import MailParser
except ImportError:
    from mail_parser import MailParser


class MailConsoleApp:
    def __init__(self, input_path: str, output_path: str) -> None:
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)

    def run(self) -> int:
        if not self.input_path.exists():
            print(f"Путь не найден: {self.input_path}")
            return 1

        mail_files = self._collect_files()
        json_path = self._json_path()
        json_path.parent.mkdir(parents=True, exist_ok=True)

        mails = []
        errors = []

        for mail_file in mail_files:
            try:
                parser = MailParser(str(mail_file))
                mail_json = parser.convert_to_json()
                mail_json["file_name"] = mail_file.name
                mails.append(mail_json)
            except (OSError, UnicodeDecodeError, ValueError) as error:
                errors.append(
                    {
                        "file_name": mail_file.name,
                        "error": str(error),
                    }
                )

        json_path.write_text(
            json.dumps(mails, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )

        if errors:
            error_path = json_path.with_name("parse_errors.json")
            error_path.write_text(
                json.dumps(errors, ensure_ascii=False, indent=4),
                encoding="utf-8",
            )
            print(f"Ошибки сохранены: {error_path}")

        print(f"Обработано писем: {len(mails)}")
        print(f"Создан файл: {json_path}")
        return 0

    def _collect_files(self) -> list[Path]:
        if self.input_path.is_file():
            return [self.input_path]

        return sorted(self.input_path.glob("*.txt"))

    def _json_path(self) -> Path:
        if self.output_path.suffix.lower() == ".json":
            return self.output_path

        return self.output_path / "all_mails.json"


def main() -> int:
    if len(sys.argv) != 3:
        print("Использование: python app/app.py input_path output_json_or_folder")
        return 1

    app = MailConsoleApp(sys.argv[1], sys.argv[2])
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
