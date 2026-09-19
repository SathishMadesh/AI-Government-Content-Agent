import re


def _normalize(text):
    """
    Normalize text for reliable comparison.
    """

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def _event_keywords(event):
    """
    Extract meaningful keywords from an event description.
    """

    if not event:
        return []

    words = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        event.lower()
    )

    ignored_words = {
        "prime",
        "minister",
        "shri",
        "visit",
        "today",
        "will",
        "with",
        "from",
        "into",
        "over",
        "about",
        "that",
        "this"
    }

    return [
        word
        for word in words
        if word not in ignored_words
    ]


def verify_facts(facts, source_text):
    """
    Verify extracted facts against the original official source text.
    """

    source = _normalize(source_text)

    results = {}

    # ---------------------------------------------------------
    # Person
    # ---------------------------------------------------------

    if facts.get("person"):
        person = _normalize(facts["person"])

        results["person"] = person in source

    # ---------------------------------------------------------
    # Country
    # ---------------------------------------------------------

    if facts.get("country"):
        country = _normalize(facts["country"])

        results["country"] = country in source

    # ---------------------------------------------------------
    # Speaker
    # ---------------------------------------------------------

    if facts.get("speaker"):
        speaker = _normalize(facts["speaker"])

        results["speaker"] = speaker in source

    # ---------------------------------------------------------
    # Event
    # ---------------------------------------------------------

    if facts.get("event"):

        keywords = _event_keywords(
            facts["event"]
        )

        if keywords:

            matched_keywords = sum(
                keyword in source
                for keyword in keywords
            )

            # Require at least half of the meaningful
            # event keywords to be present in the source.
            required_matches = max(
                1,
                len(keywords) // 2
            )

            results["event"] = (
                matched_keywords >= required_matches
            )

        else:

            results["event"] = False

    # ---------------------------------------------------------
    # Date
    # ---------------------------------------------------------

    if facts.get("date"):
        date = _normalize(facts["date"])

        results["date"] = date in source

    # ---------------------------------------------------------
    # Overall verification
    # ---------------------------------------------------------

    applicable_results = [
        value
        for key, value in results.items()
        if key != "verified"
    ]

    results["verified"] = (
        bool(applicable_results)
        and all(applicable_results)
    )

    return results
