import os
import json
import re
import httpx
from dotenv import load_dotenv


load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

OLLAMA_URL = "https://ollama.com/api/chat"


def check_relevance(title, source_text):

    prompt = f"""
You are a STRICT news editor for an Indian government
information Instagram page.

Your job is to classify an official government news release.

IMPORTANT:
Most official news releases should NOT become Instagram posts.

We only want news that would be genuinely useful and important
for the general public.

Classify the news based on whether it is suitable for
an official Indian government information Instagram page.

Use exactly ONE of these categories:

HIGH_PRIORITY:
News with major public significance, such as:

- Major government policy or national announcement
- New scheme, programme or initiative affecting citizens
- Major infrastructure development
- Important economic decision
- Major international agreement or diplomatic development
- Significant defence or national security development
- Major science, technology or space achievement
- Important education, healthcare or welfare initiative
- Major national achievement
- Important announcement directly affecting citizens

LOW_PRIORITY:
Official government news that is still meaningful,
informative, timely, or interesting to the general public,
but does not have major national significance.

Examples can include:

- Important speeches or public messages
- PM/President/minister statements with public relevance
- Visits or meetings involving meaningful developments
- Cultural or national events with public interest
- Sports achievements officially congratulated by the government
- Significant condolences or messages concerning major events
- Individual or team achievements of national interest
- Important ceremonial events
- Other legitimate government news that people may reasonably
  want to know about

NOT_RELEVANT:
Use this only when the release is clearly unsuitable
for a public-facing Instagram post.

Examples:

- Administrative appointments
- Tender notices
- Procurement notices
- Internal departmental updates
- Purely technical or administrative notices
- Duplicate or repeated information
- Content with no meaningful public information

IMPORTANT RULES:

1. Do not mark a release NOT_RELEVANT merely because it is
   not a major national announcement.

2. When a release is legitimate government information and
   has reasonable public or national interest, prefer
   LOW_PRIORITY rather than NOT_RELEVANT.

3. Do not classify something as HIGH_PRIORITY merely because
   a senior government official attended it.

4. A speech or visit can be LOW_PRIORITY when it contains
   meaningful information for the public.

5. Use NOT_RELEVANT sparingly and only when the content has
   little or no value as a public-facing government update.

Return ONLY valid JSON.

Use exactly this format:

{{
    "priority": "HIGH_PRIORITY",
    "reason": "short explanation"
}}

TITLE:
{title}

OFFICIAL NEWS:
{source_text[:6000]}
"""

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    response = httpx.post(
        OLLAMA_URL,
        headers=headers,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    content = data["message"]["content"].strip()

    print("\nRAW RELEVANCE RESPONSE:")
    print(content)
    print("\nEND RAW RESPONSE\n")

    # Remove Markdown code fences
    content = re.sub(
        r"^```json\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(
        r"^```\s*",
        "",
        content
    )

    content = re.sub(
        r"\s*```$",
        "",
        content
    ).strip()

    result = json.loads(content)

    # Safety check
    allowed_priorities = [
        "HIGH_PRIORITY",
        "LOW_PRIORITY",
        "NOT_RELEVANT"
    ]

    if result.get("priority") not in allowed_priorities:
        result["priority"] = "LOW_PRIORITY"

    return result