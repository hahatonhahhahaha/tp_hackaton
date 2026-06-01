from pathlib import Path

from app.mail_parser import MailParser


def create_mail_file(tmp_path, text: str) -> Path:
    file_path = tmp_path / "mail.txt"
    file_path.write_text(text, encoding="utf-8")
    return file_path


def test_parse_russian_mail(tmp_path):
    file_path = create_mail_file(
        tmp_path,
        """От кого: Юлия Кириллова <yu.kirillova@company.ru>
Кому: it-support@company.ru
Дата: 18.05.2025 08:40
Тема: Правки к инструкцию

Во вложении новая версия инструкции.
Вложение: invoice.pdf
        """,
    )

    parser = MailParser(str(file_path))
    result = parser.convert_to_json()

    assert result["from"] == "Юлия Кириллова <yu.kirillova@company.ru>"
    assert result["to"] == "it-support@company.ru"
    assert result["date"] == "18.05.2025 08:40"
    assert result["subject"] == "Правки к инструкцию"
    assert result["text"] == "Во вложении новая версия инструкции.\nВложение: invoice.pdf"
    assert result["attachments"] == ["invoice.pdf"]
    assert result["links"] == []


def test_parse_english_mail(tmp_path):
    file_path = create_mail_file(
        tmp_path,
        """Subject: 
From: t.andreev@company.ru

Перейдите по ссылке: http://totally-not-spam.ru/prize
        """,
    )

    parser = MailParser(str(file_path))
    result = parser.convert_to_json()

    assert result["subject"] == ""
    assert result["from"] == "t.andreev@company.ru"
    assert result["links"] == ["http://totally-not-spam.ru/prize"]
    assert result["attachments"] == []

