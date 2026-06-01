import re
from pathlib import Path


class MailParser:
    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.text = self.file_path.read_text(encoding="utf-8")

    def convert_to_json(self) -> dict:
        headers_text, body = self._split_headers_and_body()
        headers = self._parse_headers(headers_text)
        return {
            "subject": headers.get("subject", ""),
            "from": headers.get("from", ""),
            "to": headers.get("to", ""),
            "date": headers.get("date", ""),
            "text": body.strip(),
            "links": self._find_links(body),
            "attachments": self._find_attachments(body),
        }

    def _split_headers_and_body(self) -> tuple[str, str]:
        text = self.text.replace("\r\n", "\n").replace("\r", "\n")
        parts = text.split("\n\n", 1)
        if len(parts) == 2:
            return (parts[0], parts[1])
        return (text, "")

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
            line = line.strip()
            if ":" not in line:
                continue
            header, content = line.split(":", 1)
            header = header.strip().lower()
            if header in names:
                result[names[header]] = content.strip()
        return result

    def _find_links(self, body: str) -> list[str]:
        return re.findall(r"https?://\S+", body)
    
    def _find_attachments(self, body: str) -> list[str]:
        return re.findall(r"\b[\w.-]+\.(?:pdf|docx|doc|xlsx|xls|txt|zip|rar|png|jpg|jpeg)\b", body, flags=re.IGNORECASE)

    def _find_attachments(self, body: str) -> list[str]:
        return re.findall(
            r"\b[\w.-]+\.(?:pdf|docx|doc|xlsx|xls|txt|zip|rar|png|jpg|jpeg)\b",
            body,
            flags=re.IGNORECASE,
        )
