import re
from difflib import SequenceMatcher


def normalize_title(title):

    if not title:
        return ""

    title = title.lower()

    # Remove punctuation
    title = re.sub(
        r"[^a-z0-9\s]",
        " ",
        title
    )

    # Remove extra spaces
    title = re.sub(
        r"\s+",
        " ",
        title
    ).strip()

    return title


def calculate_similarity(
    title1,
    title2
):

    title1 = normalize_title(title1)
    title2 = normalize_title(title2)

    return SequenceMatcher(
        None,
        title1,
        title2
    ).ratio()


def is_duplicate(
    title,
    existing_titles,
    threshold=0.80
):

    for existing in existing_titles:

        similarity = calculate_similarity(
            title,
            existing
        )

        if similarity >= threshold:

            return {
                "duplicate": True,
                "similar_title": existing,
                "similarity": round(
                    similarity,
                    2
                )
            }

    return {
        "duplicate": False,
        "similar_title": None,
        "similarity": 0
    }