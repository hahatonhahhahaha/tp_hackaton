import json
import sys
from pathlib import Path


CLASSIFIER_DIR = Path(__file__).resolve().parents[1] / "classifier"
sys.path.insert(0, str(CLASSIFIER_DIR))

from json_uploader import json_uploader  # noqa: E402
from main import move_email_files  # noqa: E402
from score import classify_emails, load_weight  # noqa: E402


def test_classifier_uses_mail_text_and_moves_files(tmp_path):
    input_folder = tmp_path / "inbox"
    output_folder = tmp_path / "sorted"
    input_folder.mkdir()

    test_mails = [
        {
            "file_name": "mail_0001.txt",
            "subject": "Обращение 1",
            "from": "user@company.ru",
            "to": "it-support@company.ru",
            "date": "2026-06-01",
            "text": "После обновления системы пропал доступ к VPN.",
            "links": [],
        },
        {
            "file_name": "mail_0002.txt",
            "subject": "Обращение 2",
            "from": "hr@company.ru",
            "to": "it-support@company.ru",
            "date": "2026-06-01",
            "text": "Прошу выдать доступ к почте для нового сотрудника.",
            "links": [],
        },
        {
            "file_name": "mail_0003.txt",
            "subject": "Обращение 3",
            "from": "spam@example.com",
            "to": "it-support@company.ru",
            "date": "2026-06-01",
            "text": "Подтвердить доступ можно после ввода данных банковской карты.",
            "links": ["https://example.com/login"],
        },
        {
            "file_name": "mail_0004.txt",
            "subject": "Обращение 4",
            "from": "office@company.ru",
            "to": "it-support@company.ru",
            "date": "2026-06-01",
            "text": "Устройство: принтер. Не определяется системой.",
            "links": [],
        },
        {
            "file_name": "mail_0005.txt",
            "subject": "Обращение 5",
            "from": "manager@company.ru",
            "to": "it-support@company.ru",
            "date": "2026-06-01",
            "text": "Коллеги, предлагаю обсудить план встречи завтра.",
            "links": [],
        },
    ]

    for mail in test_mails:
        mail_file = input_folder / mail["file_name"]
        mail_file.write_text(mail["text"], encoding="utf-8")

    json_path = tmp_path / "all_mails.json"
    json_path.write_text(
        json.dumps(test_mails, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )

    csv_path = tmp_path / "config.csv"
    csv_path.write_text(
        "marker,incidents,service_requests,spam,hardware_faults\n"
        "после обновления системы,12,-3,-3,-3\n"
        "пропал доступ к vpn,20,-3,-3,-3\n"
        "прошу выдать доступ,-3,20,-3,-3\n"
        "нового сотрудника,-3,14,-3,-3\n"
        "подтвердить доступ,-3,-3,14,-3\n"
        "данных банковской карты,-3,-3,20,-3\n"
        "устройство: принтер,-3,-3,-3,20\n"
        "не определяется системой,-3,-3,-3,14\n",
        encoding="utf-8",
    )

    emails = json_uploader(json_path)
    weight = load_weight(csv_path)
    results = classify_emails(emails, weight)

    move_email_files(
        results=results,
        input_folder=input_folder,
        output_folder=output_folder,
    )

    results_by_file = {}

    for result in results:
        results_by_file[result["file_name"]] = result

    expected_categories = {
        "mail_0001.txt": "incidents",
        "mail_0002.txt": "service_requests",
        "mail_0003.txt": "spam",
        "mail_0004.txt": "hardware_faults",
        "mail_0005.txt": "прочее",
    }

    assert len(results) == 5

    for file_name, category in expected_categories.items():
        result = results_by_file[file_name]
        moved_file = output_folder / category / file_name

        assert result["category"] == category
        assert result["move_status"] == "перемещено"
        assert Path(result["moved_to"]) == moved_file
        assert moved_file.exists()
        assert not (input_folder / file_name).exists()

    assert "пропал доступ к vpn" in results_by_file["mail_0001.txt"]["matched_text_markers"]
    assert "прошу выдать доступ" in results_by_file["mail_0002.txt"]["matched_text_markers"]
    assert "данных банковской карты" in results_by_file["mail_0003.txt"]["matched_text_markers"]
    assert "устройство: принтер" in results_by_file["mail_0004.txt"]["matched_text_markers"]
    assert results_by_file["mail_0005.txt"]["matched_text_markers"] == []
