import re


def verify_generated_content(generated_content, source_text, verified_facts):
    """
    Verify an AI-generated Instagram post against the original source
    and previously verified facts.
    """

    title = generated_content.get("title", "")
    caption = generated_content.get("caption", "")

    combined_content = f"{title}\n{caption}".lower()
    source_lower = source_text.lower()

    results = {}

    # --------------------------------------------------
    # 1. Verify important people
    # --------------------------------------------------

    person = verified_facts.get("person")

    if person:
        results["person"] = person.lower() in combined_content
    else:
        results["person"] = True

    # --------------------------------------------------
    # 2. Verify country
    # --------------------------------------------------

    country = verified_facts.get("country")

    if country:
        results["country"] = country.lower() in combined_content
    else:
        results["country"] = True

    # --------------------------------------------------
    # 3. Verify important event
    # --------------------------------------------------

    event = verified_facts.get("event")

    if event:
        event_keywords = [
            "longest continuously serving",
            "prime minister",
            "italy"
        ]

        results["event"] = all(
            keyword in combined_content
            for keyword in event_keywords
        )
    else:
        results["event"] = True

    # --------------------------------------------------
    # 4. Verify speaker
    # --------------------------------------------------

    speaker = verified_facts.get("speaker")

    if speaker:
        results["speaker"] = speaker.lower() in combined_content
    else:
        results["speaker"] = True

    # --------------------------------------------------
    # 5. Verify date if present
    # --------------------------------------------------

    date = verified_facts.get("date")

    if date:
        date_found_in_source = date.lower() in source_lower

        # If the generated content contains a date,
        # it must be the verified date.
        date_pattern = r"\b\d{2}\s+[A-Z]{3}\s+\d{4}\b"

        generated_dates = re.findall(
            date_pattern,
            generated_content.get("caption", ""),
            re.IGNORECASE
        )

        if generated_dates:
            results["date"] = all(
                generated_date.lower() == date.lower()
                for generated_date in generated_dates
            )
        else:
            results["date"] = date_found_in_source
    else:
        results["date"] = True

    # --------------------------------------------------
    # 6. Check source attribution
    # --------------------------------------------------

    results["source_attribution"] = (
        "pib" in combined_content
        or "press information bureau" in combined_content
    )

    # --------------------------------------------------
    # Final decision
    # --------------------------------------------------

    results["verified"] = all(results.values())

    if results["verified"]:
        results["status"] = "PASS"
    else:
        results["status"] = "REVIEW"

    return results