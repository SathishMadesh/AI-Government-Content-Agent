import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

OLLAMA_URL = "https://ollama.com/api/chat"


def generate_instagram_content(source_text, facts):
    prompt = f"""
You are an AI content writer for a factual Indian government information
Instagram page.

Your job is to create an original Instagram post using ONLY the verified
information provided below.

VERIFIED FACTS:
{json.dumps(facts, indent=2)}

OFFICIAL SOURCE TEXT:
{source_text}

STRICT RULES:
1. Use only information present in the source text and verified facts.
2. Do not invent facts, quotes, numbers, dates, people, or events.
3. Do not add your own political opinion.
4. Do not change the meaning of the source.
5. Do not present anything as a direct quote unless it appears in the source.
6. Write in clear and simple English.
7. Make the content suitable for an Instagram information post.
8. The post should be original wording, not a copy of the source.
9. Mention that the information comes from PIB.
10. Do not use excessive emojis or hashtags.

Return ONLY valid JSON in exactly this format:

{{
    "title": "Short Instagram post title",
    "caption": "Instagram caption"
}}
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

    print("\nRAW GEMMA RESPONSE:")
    print(content)
    print("\nEND RAW RESPONSE\n")

    # Remove Markdown code fences if Gemma adds them
    if content.startswith("```"):
        content = content.replace("```json", "", 1)
        content = content.replace("```", "", 1)
        content = content.strip()

    return json.loads(content)