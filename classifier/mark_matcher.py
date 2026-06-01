import re


def normalize_text(text: str) -> str:
    text = str(text).lower()
    text = text.replace("ё", "е")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def build_pattern(marker: str) -> str:
    pattern = re.escape(marker)
    pattern = pattern.replace(r"\ ", r"\s+")

    if re.match(r"\w", marker[0]):
        pattern = r"(?<!\w)" + pattern

    if re.match(r"\w", marker[-1]):
        pattern = pattern + r"(?!\w)"

    return pattern

def find_markers(text: str, markers: list[str]) -> list[str]:
    text = normalize_text(text)
    normalized_markers = []

    for marker in markers:
        marker = normalize_text(marker)

        if marker:
            normalized_markers.append(marker)

    normalized_markers = sorted(
        set(normalized_markers),
        key=len,
        reverse=True,
    )

    found_markers = []
    occupied_spans = []

    for marker in normalized_markers:
        pattern = build_pattern(marker)

        for match in re.finditer(pattern, text):
            start, end = match.span()
            has_overlap = False

            for occupied_start, occupied_end in occupied_spans:
                if start < occupied_end and end > occupied_start:
                    has_overlap = True
                    break

            if has_overlap:
                continue

            found_markers.append(marker)
            occupied_spans.append((start, end))
            break

    return found_markers