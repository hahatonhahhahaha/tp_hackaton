import json
import sys
from pathlib import Path

from mail_parser import MailParser


class MailConsoleApp:
    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)

    def run(self) -> None:
        if not self.file_path.exists():
            print(f"Файл не найден: {self.file_path}")
            return
        try:
            parser = MailParser(str(self.file_path))
            mail_json = parser.convert_to_json()
            print(json.dumps(mail_json, ensure_ascii=False, indent=4))
        except Exception as e:
            print(f'Ошибка: не получилось прочитать файл. Детали: {e}')



if __name__ == "__main__":
    app = MailConsoleApp(sys.argv[1])
    app.run()