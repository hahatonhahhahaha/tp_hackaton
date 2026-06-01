from pathlib import Path
import re


class MailParser:
    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.text = self.file_path.read_text(encoding="utf-8")

    def convert_to_json(self) -> dict:
        headers_text, body = self._split_headers_and_body()
        result = self._parse_headers(headers_text)
        result["text"] = body.strip()
        result["links"] = self._find_links(body)
        result["attachments"] = self._find_attachments(body)
        return result

    def _split_headers_and_body(self) -> tuple[str, str]:
        parts = self.text.split("\n\n", 1)
        if len(parts) == 2:
            return (parts[0], parts[1])
        return (self.text, "")

    def _parse_headers(self, headers_text: str) -> dict:
        result = {}
        names = {
            "subject": "subject",
            "тема": "subject",
            "from": "from",
            "от кого": "from",
            "to": "to",
            "кому": "to",
            "date": "date",
            "дата": "date",
        }
        for line in headers_text.splitlines():
            if ":" not in line:
                continue
            header, content = line.split(":", 1)
            header = header.strip().lower()
            if header in names:
                result[names.get(header)] = content
        return result

    def _find_links(self, body: str) -> list[str]:
        return re.findall(r"https?://\S+", body)
    
    def _find_attachments(self, body: str) -> list[str]:
        return re.findall(r"\b[\w.-]+\.(?:pdf|docx|doc|xlsx|xls|txt|zip|rar|png|jpg|jpeg)\b", body, flags=re.IGNORECASE)

