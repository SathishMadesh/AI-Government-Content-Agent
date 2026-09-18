from backend.app.database import get_connection
from backend.app.services.image_strategy import choose_image_strategy
from backend.app.services.visual_concept_generator import generate_visual_concept
from backend.app.services.image_generator import (
    generate_ai_background,
    generate_instagram_image
)
import json


SOURCE_POST_ID = "2308322"


# ----------------------------------------
# 1. Get source record
# ----------------------------------------

connection = get_connection()

row = connection.execute("""
    SELECT
        source_post_id,
        source_url,
        source_title,
        source_text,
        extracted_facts
    FROM content_items
    WHERE source_post_id = ?
""", (SOURCE_POST_ID,)).fetchone()

connection.close()


if not row:
    print("Record not found.")
    raise SystemExit


facts = json.loads(row["extracted_facts"])


print("\nRecord:")
print(row["source_post_id"])
print(row["source_title"])


# ----------------------------------------
# 2. Choose image strategy
# ----------------------------------------

print("\nChecking image strategy...\n")

strategy_result = choose_image_strategy(
    row["source_url"]
)

print("\nStrategy result:")
print(json.dumps(
    strategy_result,
    indent=2,
    ensure_ascii=False
))


strategy = strategy_result["strategy"]


# ----------------------------------------
# 3. Official image
# ----------------------------------------

if strategy == "OFFICIAL_IMAGE":

    image_source = strategy_result["image"]["url"]

    print("\nUsing official PIB image:")
    print(image_source)


# ----------------------------------------
# 4. AI generated image
# ----------------------------------------

else:

    print("\nNo suitable official image.")
    print("Generating visual concept...\n")

    visual_concept = generate_visual_concept(
        title=row["source_title"],
        source_text=row["source_text"],
        facts=facts
    )

    print("\nVisual concept:")
    print(json.dumps(
        visual_concept,
        indent=2,
        ensure_ascii=False
    ))

    if not visual_concept:
        print("\nVisual concept generation failed.")
        raise SystemExit

    image_prompt = visual_concept.get("image_prompt")

    if not image_prompt:
        print("\nNo image prompt generated.")
        raise SystemExit

    print("\nGenerating AI background...")

    image_source = generate_ai_background(
        image_prompt,
        SOURCE_POST_ID
    )

    if not image_source:
        print("\nAI image generation failed.")
        raise SystemExit


# ----------------------------------------
# 5. Create final Instagram image
# ----------------------------------------

print("\nCreating final Instagram image...")

final_image = generate_instagram_image(
    title=row["source_title"],
    image_source=image_source,
    source="PIB",
    source_post_id=SOURCE_POST_ID
)


# ----------------------------------------
# 6. Result
# ----------------------------------------

if final_image:

    connection = get_connection()

    connection.execute("""
        UPDATE content_items
        SET
            generated_image_path = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE source_post_id = ?
    """, (
        final_image,
        SOURCE_POST_ID
    ))

    connection.commit()
    connection.close()

    print("\nImage path saved to database.")

    print("\nSUCCESS!")
    print("Final image:")
    print(final_image)

else:

    print("\nImage generation failed.")