import re


def extract_facts(source_text):
    """
    Extract basic structured facts from a PIB/PMO release.
    """

    facts = {
        "person": None,
        "country": None,
        "event": None,
        "speaker": None,
        "date": None
    }

    if not source_text:
        return facts

    text = source_text.strip()

    # ---------------------------------------------------------
    # Date
    # ---------------------------------------------------------

    date_match = re.search(
        r"\b(\d{2}\s+[A-Z]{3}\s+\d{4})\b",
        text
    )

    if date_match:
        facts["date"] = date_match.group(1)

    # ---------------------------------------------------------
    # Speaker
    # ---------------------------------------------------------

    speaker_patterns = [
        r"Prime Minister Shri Narendra Modi",
        r"Prime Minister Narendra Modi",
        r"Shri Narendra Modi",
        r"Narendra Modi"
    ]

    for pattern in speaker_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            facts["speaker"] = "Narendra Modi"
            break

    # ---------------------------------------------------------
    # Person
    # ---------------------------------------------------------

    person_patterns = [
        r"Italian Prime Minister\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+)",
        r"President\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+)",
        r"Vice President\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+)"
    ]

    for pattern in person_patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            candidate = match.group(1).strip()

            if "Narendra Modi" not in candidate:

                facts["person"] = candidate

                break

    # ---------------------------------------------------------
    # Country
    # ---------------------------------------------------------

    country_patterns = [
        "India",
        "Italy",
        "France",
        "Germany",
        "United States",
        "United Kingdom",
        "Japan",
        "Australia",
        "Canada",
        "Russia",
        "China",
        "Brazil",
        "South Africa"
    ]

    for country in country_patterns:
        if re.search(rf"\b{re.escape(country)}\b", text, re.IGNORECASE):
            facts["country"] = country
            break

    # ---------------------------------------------------------
    # Event
    # ---------------------------------------------------------

    # Use the first meaningful title/headline line as the event.
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines:

        if len(line) < 20:
            continue

        if "Press Release Page" in line:
            continue

        if "Prime Minister's Office" in line:
            continue

        if line.startswith("Posted On:"):
            continue

        if "Visitor Counter" in line:
            continue

        facts["event"] = line
        break

    return facts
