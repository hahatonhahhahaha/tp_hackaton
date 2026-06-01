from dataclasses import dataclass, field


@dataclass
class ParsedEmail:
    file_name: str = ""
    subject: str = ""
    sender: str = ""
    recipient: str = ""
    date: str = ""
    text: str = ""
    links: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict):
        file_name = (
            raw.get("file_name")
            or raw.get("filename")
            or raw.get("file")
            or ""
        )

        return ParsedEmail(
            file_name=str(file_name).strip(),
            subject=str(raw.get("subject") or "").strip(),
            sender=str(raw.get("from") or "").strip(),
            recipient=str(raw.get("to") or "").strip(),
            date=str(raw.get("date") or "").strip(),
            text=str(raw.get("text") or "").strip(),
            links=list(raw.get("links") or []),
            attachments=list(raw.get("attachments") or []),
        )
