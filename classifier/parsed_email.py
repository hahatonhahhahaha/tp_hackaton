from dataclasses import dataclass, field

@dataclass
class ParsedEmail:
    subject: str = ''
    sender: str = ''
    recipient: str = ''
    date: str = ''
    text: str = ''
    links: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(csl, object: dict):
        return ParsedEmail(
            subject=(object.get("subject").strip()),
            sender=(object.get("from").strip()),
            recipient=(object.get("to").strip()),
            date=(object.get("date").strip()),
            text=(object.get("text").strip()),
            links=(object.get("links")),
            # filename=(object.get("filename") or object.get("file")).strip(),
        )
        
