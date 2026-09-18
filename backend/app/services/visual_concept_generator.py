
import json
import re
import httpx

from dotenv import load_dotenv


load_dotenv()


OLLAMA_MODEL = "gemma:2b"

OLLAMA_URL = (
    "http://localhost:11434/api/chat"
)


def generate_visual_concept(
    title,
    source_text,
    facts
):

    print(
        "\nGenerating visual concept..."
    )

    prompt = f"""
You are an expert visual director for a professional
Indian government news Instagram page.

Create ONE realistic static image concept for this
official news story.

NEWS TITLE:
{title}

VERIFIED FACTS:
{json.dumps(facts, indent=2)}

SOURCE TEXT:
{source_text[:4000]}

RULES:

1. Create exactly ONE single static image.
2. Focus only on the actual news topic.
3. Use only information supported by the title,
   source text, or verified facts.
4. Do not invent people, officials, locations,
   projects, buildings, vehicles, or events.
5. Do not include text, captions, logos, or
   watermarks inside the generated image.
6. Make the image realistic, professional,
   cinematic, and suitable for a government-news
   Instagram post.
7. Avoid generic futuristic AI artwork.
8. Do not create multiple scenes.
9. Do not suggest video or animation.
10. If people are not clearly supported by the source,
    do not invent identifiable people.
11. Use neutral realistic visual representations
    when specific visual details are unavailable.

The image_prompt must describe:
- the main subject
- relevant environment
- camera perspective
- realistic lighting
- mood
- editorial photography style

IMPORTANT:

Return ONLY valid JSON.

Do not use markdown.

Do not write anything before or after the JSON.

Do not use quotation marks inside the values.

Return exactly these four fields:

{{
    "category": "technology",
    "visual_concept": "One concise description of the image",
    "image_prompt": "A detailed realistic production-ready image generation prompt",
    "headline_focus": "Short visual message"
}}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.2,
            "num_predict": 500
        }
    }

    try:

        print("\nOLLAMA URL:")
        print(OLLAMA_URL)

        print("\nOLLAMA MODEL:")
        print(OLLAMA_MODEL)

        print("\nSending request to Ollama...")

        response = httpx.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        print("\nResponse Status:")
        print(response.status_code)

        response.raise_for_status()

        data = response.json()

        content = data["message"]["content"].strip()

        print(
            "\nRAW VISUAL RESPONSE:"
        )

        print(content)

        print(
            "\nEND RAW RESPONSE\n"
        )

        # ============================================
        # CLEAN GEMMA RESPONSE
        # ============================================

        # Remove markdown code fences if Gemma adds them.
        content = content.replace(
            "```json",
            ""
        )

        content = content.replace(
            "```JSON",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        content = content.strip()

        # ============================================
        # FIND JSON OBJECT
        # ============================================

        start = content.find("{")
        end = content.rfind("}")

        print(
            f"\nJSON start position: {start}"
        )

        print(
            f"JSON end position: {end}"
        )

        if start == -1 or end == -1 or end <= start:

            print(
                "\nCould not locate JSON object."
            )

            print(
                "\nRaw content representation:"
            )

            print(
                repr(content)
            )

            raise ValueError(
                "No valid JSON object found in Gemma response."
            )

        json_text = content[
            start:end + 1
        ]

        print(
            "\nExtracted JSON:"
        )

        print(
            json_text
        )

        # ============================================
        # PARSE JSON
        # ============================================

        result = json.loads(
            json_text
        )

        # ============================================
        # VALIDATE FIELDS
        # ============================================

        required_fields = [
            "category",
            "visual_concept",
            "image_prompt",
            "headline_focus"
        ]

        for field in required_fields:

            if field not in result:

                raise ValueError(
                    f"Missing required field: {field}"
                )

            if not result[field]:

                raise ValueError(
                    f"Empty value for field: {field}"
                )

        print(
            "\nVisual concept successfully generated."
        )

        print(
            "\nImage prompt:"
        )

        print(
            result["image_prompt"]
        )

        return result

    except Exception as error:

        print(
            "\nError generating visual concept:"
        )

        print(
            error
        )

        return None
