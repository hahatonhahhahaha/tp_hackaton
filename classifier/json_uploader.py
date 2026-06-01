# import json
# from pathlib import Path

# from parsed_email import ParsedEmail


# def json_uploader(json_path: str | Path) -> list[ParsedEmail]:
#     json_path = Path(json_path)

#     if not json_path.exists():
#         raise FileNotFoundError(f'Файл({json_path.name}) не найден: \
#                                 в {json_path.parent}')
    
#     with json_path.open('r', encoding='utf-8') as json_file:
#         data = json.load(json_file)

#         if not isinstance(data, list):
#             raise ValueError("JSON must be a list")
        
#         emails: list[ParsedEmail] = []

#         for obj in data:
#             email = ParsedEmail.from_dict(obj)
#             emails.append(email)

#         return emails


# print(json_uploader('/Users/areluv/Downloads/hahaton/tp_hackaton/classifier/test.json'))

import json
from pathlib import Path

from parsed_email import ParsedEmail


def json_uploader(json_path: str | Path) -> list[ParsedEmail]:
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(
            f"Файл ({json_path.name}) не найден в {json_path.parent}"
        )

    with json_path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)

        if not isinstance(data, list):
            raise ValueError("JSON должен быть списком")

        emails: list[ParsedEmail] = []

        for obj in data:
            email = ParsedEmail.from_dict(obj)
            emails.append(email)

        return emails