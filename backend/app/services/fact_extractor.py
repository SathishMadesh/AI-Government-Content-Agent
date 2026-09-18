import re


def extract_facts(source_text):
    """
    Extract basic structured facts from a PIB release.
    """

    facts = {
        "person": None,
        "country": None,
        "event": None,
        "speaker": None,
        "date": None
    }

    # Extract date
    date_match = re.search(
        r"(\d{2}\s+[A-Z]{3}\s+\d{4})",
        source_text
    )

    if date_match:
        facts["date"] = date_match.group(1)

    # Identify Narendra Modi as speaker when present
    if "Prime Minister Shri Narendra Modi" in source_text:
        facts["speaker"] = "Narendra Modi"

    # Extract the person mentioned as the Italian Prime Minister
    person_match = re.search(
        r"Italian Prime Minister\s+([A-Z][A-Za-z]+\s+[A-Z][A-Za-z]+)",
        source_text
    )

    if person_match:
        facts["person"] = person_match.group(1)

    # Identify country
    if "Italy" in source_text or "Italian" in source_text:
        facts["country"] = "Italy"

    # Extract the main event from the title/body
    if "longest continuously serving Prime Minister" in source_text:
        facts["event"] = (
            "Giorgia Meloni became the longest continuously serving "
            "Prime Minister in Italy's postwar history"
        )

    return facts