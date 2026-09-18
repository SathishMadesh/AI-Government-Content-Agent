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

Classify the news into exactly ONE of these categories:

HIGH_PRIORITY:
Use only when the news includes something significant such as:

- Major government policy or national announcement
- New scheme, programme or initiative affecting the public
- Major infrastructure project with significant public impact
- Important economic decision
- Major international agreement or diplomatic development
- Significant defence or national security announcement
- Major science, technology or space achievement
- Important education, healthcare or welfare initiative
- Major national achievement
- Important announcement directly affecting citizens

LOW_PRIORITY:
Official news that may be interesting but does not justify
a dedicated Instagram post.

Examples:

- Routine speeches
- Visits to institutions
- Ceremonial events
- Cultural events
- Routine meetings
- Foundation stone ceremonies without major public impact
- Greetings and congratulatory messages
- Individual awards or celebrations
- General statements without new announcements
- Routine government events

NOT_RELEVANT:

- Administrative appointments
- Press communiques without useful public information
- Internal departmental updates
- Tender notices
- Procurement notices
- Repeated information
- Technical or administrative notices

IMPORTANT RULES:

1. Do NOT classify something HIGH_PRIORITY just because
   the President, Prime Minister or Vice-President attended it.

2. A speech is NOT HIGH_PRIORITY unless it contains
   a major new government announcement or policy.

3. A visit is NOT HIGH_PRIORITY unless it announces
   a significant development affecting the public.

4. Ceremonies and greetings are usually LOW_PRIORITY.

5. Be selective. HIGH_PRIORITY should be rare.

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