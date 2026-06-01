import importlib
import json
import sys
from pathlib import Path
from textwrap import dedent
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
CLASSIFIER_DIR = ROOT_DIR / "classifier"
sys.path.insert(0, str(CLASSIFIER_DIR))

MailConsoleApp = importlib.import_module("app.app").MailConsoleApp
MailParser = importlib.import_module("app.mail_parser").MailParser
json_uploader = importlib.import_module("json_uploader").json_uploader
run_classifier = importlib.import_module("main").run_classifier
score = importlib.import_module("score")
classify_emails = score.classify_emails
load_weight = score.load_weight


def write_mail(path: Path, text: str) -> None:
    path.write_text(dedent(text).strip(), encoding="utf-8")


def test_parser_reads_headers_text_links_and_attachments(tmp_path):
    mail_path = tmp_path / "mail.txt"
    write_mail(
        mail_path,
        """
        От кого: Юлия Кириллова <yu.kirillova@company.ru>
        Кому: it-support@company.ru
        Дата: 18.05.2025 08:40
        Тема: Правки к инструкции
        Строка без двоеточия

        Во вложении новая версия инструкции.
        Ссылка: https://company.ru/docs
        Вложение: invoice.pdf
        """,
    )

    result = MailParser(str(mail_path)).convert_to_json()

    assert result["from"] == "Юлия Кириллова <yu.kirillova@company.ru>"
    assert result["to"] == "it-support@company.ru"
    assert result["date"] == "18.05.2025 08:40"
    assert result["subject"] == "Правки к инструкции"
    assert "новая версия инструкции" in result["text"]
    assert result["links"] == ["https://company.ru/docs"]
    assert result["attachments"] == ["invoice.pdf"]


def test_classifier_handles_main_categories_and_other(tmp_path):
    json_path = tmp_path / "all_mails.json"
    json_path.write_text(
        json.dumps(
            [
                {
                    "file_name": "mail_0001.txt",
                    "subject": "Падает сервис",
                    "from": "user@company.ru",
                    "to": "it-support@company.ru",
                    "date": "2026-06-01",
                    "text": "Критический инцидент ошибка 500 работа остановлена.",
                    "links": [],
                    "attachments": [],
                },
                {
                    "file_name": "mail_0002.txt",
                    "subject": "Нужен доступ",
                    "from": "hr@company.ru",
                    "to": "it-support@company.ru",
                    "date": "2026-06-01",
                    "text": "Прошу выдать доступ к почте для нового сотрудника.",
                    "links": [],
                    "attachments": [],
                },
                {
                    "file_name": "mail_0003.txt",
                    "subject": "Подарок",
                    "from": "spam@example.com",
                    "to": "it-support@company.ru",
                    "date": "2026-06-01",
                    "text": "Подтвердить доступ после ввода данных банковской карты.",
                    "links": ["https://example.com/login"],
                    "attachments": [],
                },
                {
                    "file_name": "mail_0004.txt",
                    "subject": "Неисправность оборудования",
                    "from": "office@company.ru",
                    "to": "it-support@company.ru",
                    "date": "2026-06-01",
                    "text": "Устройство: принтер. Не определяется системой.",
                    "links": [],
                    "attachments": [],
                },
                {
                    "file_name": "mail_0005.txt",
                    "subject": "Встреча",
                    "from": "manager@company.ru",
                    "to": "it-support@company.ru",
                    "date": "2026-06-01",
                    "text": "Коллеги, предлагаю обсудить план встречи завтра.",
                    "links": [],
                    "attachments": [],
                },
            ],
            ensure_ascii=False,
            indent=4,
        ),
        encoding="utf-8",
    )

    emails = json_uploader(json_path)
    weight = load_weight(ROOT_DIR / "classifier" / "config.csv")
    results = classify_emails(emails, weight)
    by_file = {result["file_name"]: result for result in results}

    assert by_file["mail_0001.txt"]["category"] == "incidents"
    assert by_file["mail_0002.txt"]["category"] == "service_requests"
    assert by_file["mail_0003.txt"]["category"] == "spam"
    assert by_file["mail_0004.txt"]["category"] == "hardware_faults"
    assert by_file["mail_0005.txt"]["category"] == "прочее"
    assert by_file["mail_0005.txt"]["decision_reason"]


def test_full_pipeline_parses_classifies_and_moves_files(tmp_path):
    input_folder = tmp_path / "inbox"
    output_folder = tmp_path / "sorted"
    input_folder.mkdir()
    output_folder.mkdir()

    write_mail(
        input_folder / "mail_0001.txt",
        """
        From: user@company.ru
        To: it-support@company.ru
        Date: 2026-06-01
        Subject: Падает система

        Критический инцидент ошибка 500 работа остановлена.
        """,
    )
    write_mail(
        input_folder / "mail_0002.txt",
        """
        От кого: hr@company.ru
        Кому: it-support@company.ru
        Дата: 2026-06-01
        Тема: Новый сотрудник

        Прошу выдать доступ к почте для нового сотрудника.
        """,
    )
    write_mail(
        input_folder / "mail_0003.txt",
        """
        Subject: Письмо без категории

        Коллеги, предлагаю обсудить план встречи завтра.
        """,
    )

    json_path = output_folder / "all_mails.json"
    result_path = output_folder / "result.json"

    assert MailConsoleApp(str(input_folder), str(json_path)).run() == 0

    results = run_classifier(json_path, input_folder, output_folder, result_path)
    by_file = {result["file_name"]: result for result in results}

    assert by_file["mail_0001.txt"]["category"] == "incidents"
    assert by_file["mail_0002.txt"]["category"] == "service_requests"
    assert by_file["mail_0003.txt"]["category"] == "прочее"
    assert (output_folder / "incidents" / "mail_0001.txt").exists()
    assert (output_folder / "service_requests" / "mail_0002.txt").exists()
    assert (output_folder / "прочее" / "mail_0003.txt").exists()
    assert not (input_folder / "mail_0001.txt").exists()
    assert result_path.exists()


def test_json_uploader_accepts_utf8_bom(tmp_path):
    json_path = tmp_path / "mail.json"
    data = [{"file_name": "mail.txt", "subject": "Тест", "text": "ошибка 500"}]
    json_path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8-sig",
    )

    emails = json_uploader(json_path)

    assert len(emails) == 1
    assert emails[0].file_name == "mail.txt"

def test_json_uploader_rejects_invalid_json(tmp_path):
    json_path = tmp_path / "broken.json"
    json_path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        json_uploader(json_path)