import json
import sys
from pathlib import Path

from mail_parser import MailParser


class MailConsoleApp:
    def __init__(self, input_folder: str, output_folder: str) -> None:
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)

    def run(self) -> None:
        if not self.input_folder.exists():
            print(f"Папка не найдена: {self.input_folder}")
            return
        if not self.input_folder.is_dir():
            print(f"Это не папка: {self.input_folder}")
            return
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        all_mails = []
        mail_files = sorted(self.input_folder.glob("*.txt"))
        for mail_file in mail_files:
            mail_json  = self._convert_file(mail_file)
            if mail_json:
                all_mails.append(mail_json)
        
        json_file_path = self.output_folder / "all_mails.json"
        json_file_path.write_text(
            json.dumps(all_mails, ensure_ascii=False, indent=4),
            encoding="utf-8",
            )
        print(f"Создан общий файл: {json_file_path}")
        
    def _convert_file(self, mail_file: Path) -> None:
        try:
            parser = MailParser(str(mail_file))
            mail_json = parser.convert_to_json()
            mail_json["file_name"] = mail_file.name
            return mail_json
        except Exception as e:
            print(f'Ошибка: не получилось прочитать файл. Детали: {e}')
            return None
        


if __name__ == "__main__":
    app = MailConsoleApp(sys.argv[1], sys.argv[2])
    app.run()
