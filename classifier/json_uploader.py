import json
from pathlib import Path

from parsed_email import ParsedEmail


def json_uploader(json_path: str | Path) -> list[ParsedEmail]:
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"Файл не найден: {json_path}")

    with json_path.open("r", encoding="utf-8-sig") as json_file:
        data = json.load(json_file)

    if not isinstance(data, list):
        raise ValueError("JSON должен быть списком")

    emails: list[ParsedEmail] = []

    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Каждое письмо должно быть словарем")
        emails.append(ParsedEmail.from_dict(item))

    return emails
