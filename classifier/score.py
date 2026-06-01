import csv
from pathlib import Path

from parsed_email import ParsedEmail
from mark_matcher import find_markers, normalize_text


CATEGORIES = [
    "incidents",
    "service_requests",
    "spam",
    "hardware_faults",
]
OTHER_CATEGORY = "прочее"
TEXT_MULTIPLIER = 1
SUBJECT_MULTIPLIER = 2.5
MIN_MARGIN = 4
CATEGORY_THRESHOLDS = {
    "incidents": 10,
    "service_requests": 10,
    "spam": 12,
    "hardware_faults": 10,
}


def load_weight(csv_path: str | Path) -> dict[str, dict[str, int]]:
    csv_path = Path(csv_path)
    weight: dict[str, dict[str, int]] = {}

    with csv_path.open("r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
    
        for row in reader:
            marker = normalize_text(row["marker"])
            weight[marker] = {}

            for category in CATEGORIES:
                weight[marker][category] = int(row[category])

    return weight


def make_empty_scores() -> dict[str, float]:
    scores: dict[str, float] = {}

    for category in CATEGORIES:
        scores[category] = 0

    return scores


def add_marker_score(
    scores: dict[str, float],
    marker: str,
    source: str,
    multiplier: float,
    weight: dict[str, dict[str, int]],
    evidence: list[dict],) -> None:

    marker_weight = weight[marker]
    added_scores: dict[str, float] = {}

    for category in CATEGORIES:
        added_score = marker_weight[category] * multiplier
        scores[category] += added_score
        added_scores[category] = added_score

    evidence.append(
        {
            "marker": marker,
            "source": source,
            "multiplier": multiplier,
            "added_scores": added_scores,
        }
    )


def calculate_scores(
    subject_markers: list[str],
    text_markers: list[str],
    weight: dict[str, dict[str, int]]) -> \
        tuple[dict[str, float], list[dict]]:
    
    scores = make_empty_scores()
    evidence: list[dict] = []

    for marker in text_markers:
        add_marker_score(
            scores=scores,
            marker=marker,
            source="text",
            multiplier=TEXT_MULTIPLIER,
            weight=weight,
            evidence=evidence,
        )

    for marker in subject_markers:
        add_marker_score(
            scores=scores,
            marker=marker,
            source="subject",
            multiplier=SUBJECT_MULTIPLIER,
            weight=weight,
            evidence=evidence,
        )

    return scores, evidence


def choose_category(scores: dict[str, float]) -> tuple[str, str]:
    sorted_scores = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    best_category, best_score = sorted_scores[0]
    second_category, second_score = sorted_scores[1]

    if best_score < CATEGORY_THRESHOLDS[best_category]:
        return (
            OTHER_CATEGORY,
            f"Лучший результат у категории '{best_category}' = {best_score}, "
            f"но нужен минимум {CATEGORY_THRESHOLDS[best_category]}",
        )

    if best_score - second_score < MIN_MARGIN:
        return (
            OTHER_CATEGORY,
            f"Слишком маленький отрыв: "
            f"{best_category}={best_score}, {second_category}={second_score}",
        )

    return (
        best_category,
        f"Выбрана категория '{best_category}', score={best_score}, "
        f"отрыв от второго места={best_score - second_score}",
    )


def classify_email(
    email: ParsedEmail,
    weight: dict[str, dict[str, int]],
) -> dict:
    markers = list(weight.keys())

    subject_markers = find_markers(email.subject, markers)
    text_markers = find_markers(email.text, markers)

    scores, evidence = calculate_scores(
        subject_markers=subject_markers,
        text_markers=text_markers,
        weight=weight,
    )

    category, decision_reason = choose_category(scores)

    return {
        "subject": email.subject,
        "sender": email.sender,
        "recipient": email.recipient,
        "date": email.date,
        "text": email.text,
        "links": email.links,
        "category": category,
        "scores": scores,
        "matched_subject_markers": subject_markers,
        "matched_text_markers": text_markers,
        "evidence": evidence,
        "decision_reason": decision_reason,
    }


def classify_emails(
    emails: list[ParsedEmail],
    weight: dict[str, dict[str, int]],
) -> list[dict]:
    results = []

    for email in emails:
        result = classify_email(email, weight)
        results.append(result)

    return results