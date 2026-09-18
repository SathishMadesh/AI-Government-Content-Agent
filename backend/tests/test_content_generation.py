from backend.app.database import get_connection
from backend.app.services.content_generator import generate_instagram_content
from backend.app.services.generated_content_verifier import verify_generated_content
import json


SOURCE_POST_ID = "2311294"


# ----------------------------------------
# 1. Get existing record
# ----------------------------------------

connection = get_connection()

row = connection.execute("""
    SELECT
        source_post_id,
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


print("\nRecord found:")
print(row["source_post_id"])
print(row["source_title"])


# ----------------------------------------
# 2. Load extracted facts
# ----------------------------------------

facts = json.loads(
    row["extracted_facts"]
)

print("\nExtracted facts:")
print(json.dumps(facts, indent=2))


# ----------------------------------------
# 3. Generate Instagram content
# ----------------------------------------

print("\nGenerating Instagram content...\n")

generated_content = generate_instagram_content(
    source_text=row["source_text"],
    facts=facts
)


print("\nGenerated content:")
print(json.dumps(
    generated_content,
    indent=2,
    ensure_ascii=False
))


# ----------------------------------------
# 4. Verify generated content
# ----------------------------------------

print("\nVerifying generated content...\n")

verification_result = verify_generated_content(
    generated_content,
    row["source_text"],
    facts
)


print("Verification result:")
print(json.dumps(
    verification_result,
    indent=2
))


# ----------------------------------------
# 5. Final result
# ----------------------------------------

if verification_result.get("verified"):

    print("\nSUCCESS: Generated content PASSED verification.")

else:

    print("\nREVIEW REQUIRED: Generated content FAILED verification.")