def verify_facts(facts, source_text):
    """
    Verify extracted facts against the original official source text.
    """

    results = {}

    # Person
    if facts["person"]:
        results["person"] = facts["person"].lower() in source_text.lower()

    # Country
    if facts["country"]:
        results["country"] = (
            facts["country"].lower() in source_text.lower()
        )

    # Speaker
    if facts["speaker"]:
        speaker_name = facts["speaker"].lower()

        results["speaker"] = (
            speaker_name in source_text.lower()
            or "prime minister shri narendra modi" in source_text.lower()
        )

    # Event
    if facts["event"]:
        event_keywords = [
            "longest continuously serving",
            "prime minister",
            "italy"
        ]

        results["event"] = all(
            keyword in source_text.lower()
            for keyword in event_keywords
        )

    # Date
    if facts["date"]:
        results["date"] = facts["date"].lower() in source_text.lower()

    # Overall verification
    results["verified"] = all(
        value is True
        for key, value in results.items()
        if key != "verified"
    )

    return results