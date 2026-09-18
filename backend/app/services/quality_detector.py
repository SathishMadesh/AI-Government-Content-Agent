import re


def check_content_quality(title, source_text):

    # Empty title
    if not title or not title.strip():

        return {
            "quality": "REJECTED",
            "reason": "Empty title"
        }


    # Source text too short
    if not source_text or len(
        source_text.strip()
    ) < 200:

        return {
            "quality": "REJECTED",
            "reason": "Source text too short"
        }


    title_lower = title.lower()


    # Speech translations
    rejected_patterns = [

        "english rendering of",
        "hindi rendering of",
        "speech during",
        "transcript of",
        "full text of",
        "press communique",
        "press communiqué"

    ]


    for pattern in rejected_patterns:

        if pattern in title_lower:

            return {
                "quality": "REJECTED",
                "reason": f"Low value content: {pattern}"
            }


    # Greetings
    greeting_patterns = [

        "greetings on",
        "congratulates",
        "extends greetings",
        "pays floral tributes"

    ]


    for pattern in greeting_patterns:

        if pattern in title_lower:

            return {
                "quality": "REJECTED",
                "reason": f"Greeting or ceremonial content: {pattern}"
            }


    return {
        "quality": "PASSED",
        "reason": "Content passed quality checks"
    }