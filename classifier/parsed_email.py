from dataclasses import dataclass, field

@dataclass
class ParsedEmail:
    file_name: str = ''
    subject: str = ''
    sender: str = ''
    recipient: str = ''
    date: str = ''
    text: str = ''
    links: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, object: dict):
        file_name = (
            object.get("file_name")
            or object.get("filename")
            or object.get("file")
            or ""
        )

        return ParsedEmail(
            file_name=str(file_name).strip(),
            subject=str(object.get("subject") or "").strip(),
            sender=str(object.get("from") or "").strip(),
            recipient=str(object.get("to") or "").strip(),
            date=str(object.get("date") or "").strip(),
            text=str(object.get("text") or "").strip(),
            links=object.get("links") or [],
        )
