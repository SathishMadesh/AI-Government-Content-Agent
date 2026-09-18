
import json

from backend.app.database import get_connection

from backend.app.services.content_service import (
    save_extracted_facts,
    save_generated_content,
    update_verification_status,
    generate_content_image,
    send_for_approval
)

from backend.app.services.fact_extractor import (
    extract_facts
)

from backend.app.services.content_generator import (
    generate_instagram_content
)

from backend.app.services.generated_content_verifier import (
    verify_generated_content
)


SOURCE_POST_ID = "2311294"


# ============================================
# GET EXISTING PIB RECORD
# ============================================

print("\n========================================")
print("FULL PIPELINE TEST")
print("========================================")


connection = get_connection()

row = connection.execute("""
    SELECT
        source_post_id,
        source_url,
        source_title,
        source_text
    FROM content_items
    WHERE source_post_id = ?
""", (SOURCE_POST_ID,)).fetchone()

connection.close()


if not row:

    print("\nERROR: Record not found.")

    raise SystemExit


source_post_id = row["source_post_id"]
source_url = row["source_url"]
source_title = row["source_title"]
source_text = row["source_text"]


print("\nRecord found:")

print(
    f"Source Post ID : {source_post_id}"
)

print(
    f"Source Title   : {source_title}"
)


# ============================================
# RESET TEST STATUS
# ============================================

print("\n========================================")
print("RESETTING TEST RECORD")
print("========================================")


connection = get_connection()

connection.execute("""
    UPDATE content_items
    SET
        verification_status = 'FACTS_EXTRACTED',
        generated_title = NULL,
        generated_caption = NULL,
        generated_image_path = NULL,
        approval_status = 'PENDING',
        updated_at = CURRENT_TIMESTAMP
    WHERE source_post_id = ?
""", (SOURCE_POST_ID,))

connection.commit()
connection.close()


print("\nTest record reset.")


# ============================================
# STEP 1 — EXTRACT FACTS
# ============================================

print("\n========================================")
print("STEP 1 — FACT EXTRACTION")
print("========================================")


facts = extract_facts(
    source_text
)


if not facts:

    print(
        "\nERROR: Fact extraction failed."
    )

    update_verification_status(
        SOURCE_POST_ID,
        "FAILED"
    )

    raise SystemExit


print("\nExtracted facts:")

print(
    json.dumps(
        facts,
        indent=2
    )
)


save_extracted_facts(
    SOURCE_POST_ID,
    facts
)


print(
    "\nFacts saved to database."
)


# ============================================
# STEP 2 — GENERATE INSTAGRAM CONTENT
# ============================================

print("\n========================================")
print("STEP 2 — CONTENT GENERATION")
print("========================================")


generated_content = generate_instagram_content(
    source_text=source_text,
    facts=facts
)


if not generated_content:

    print(
        "\nERROR: Content generation failed."
    )

    update_verification_status(
        SOURCE_POST_ID,
        "FAILED"
    )

    raise SystemExit


print("\nGenerated content:")

print(
    json.dumps(
        generated_content,
        indent=2,
        ensure_ascii=False
    )
)


# ============================================
# STEP 3 — VERIFY GENERATED CONTENT
# ============================================

print("\n========================================")
print("STEP 3 — CONTENT VERIFICATION")
print("========================================")


verification_result = verify_generated_content(
    generated_content,
    source_text,
    facts
)


print("\nVerification result:")

print(
    json.dumps(
        verification_result,
        indent=2
    )
)


# ============================================
# SAVE GENERATED CONTENT
# ============================================

save_generated_content(
    SOURCE_POST_ID,
    generated_content
)


if not verification_result.get("verified"):

    update_verification_status(
        SOURCE_POST_ID,
        "FACT_CHECK_FAILED"
    )

    print(
        "\nERROR: Generated content failed verification."
    )

    raise SystemExit


update_verification_status(
    SOURCE_POST_ID,
    "FACT_CHECKED"
)


print(
    "\nContent verification PASSED."
)


# ============================================
# STEP 4 — GENERATE AI IMAGE
# ============================================

print("\n========================================")
print("STEP 4 — AI IMAGE GENERATION")
print("========================================")


final_image = generate_content_image(
    source_post_id=SOURCE_POST_ID,
    source_url=source_url,
    source_title=source_title,
    source_text=source_text,
    facts=facts
)


if not final_image:

    print(
        "\nERROR: Image generation failed."
    )

    update_verification_status(
        SOURCE_POST_ID,
        "FAILED"
    )

    raise SystemExit


print(
    "\nAI image generated successfully."
)

print(
    f"Image path: {final_image}"
)


# ============================================
# STEP 5 — SEND FOR APPROVAL
# ============================================

print("\n========================================")
print("STEP 5 — HUMAN APPROVAL")
print("========================================")


send_for_approval(
    SOURCE_POST_ID
)


print(
    "\nPost sent for human approval."
)


# ============================================
# STEP 6 — VERIFY FINAL DATABASE STATE
# ============================================

print("\n========================================")
print("FINAL DATABASE STATE")
print("========================================")


connection = get_connection()

final_row = connection.execute("""
    SELECT
        source_post_id,
        verification_status,
        approval_status,
        generated_title,
        generated_caption,
        generated_image_path
    FROM content_items
    WHERE source_post_id = ?
""", (SOURCE_POST_ID,)).fetchone()

connection.close()


print(
    f"\nSource Post ID      : "
    f"{final_row['source_post_id']}"
)

print(
    f"Verification Status : "
    f"{final_row['verification_status']}"
)

print(
    f"Approval Status     : "
    f"{final_row['approval_status']}"
)

print(
    f"Generated Title     : "
    f"{final_row['generated_title']}"
)

print(
    f"Generated Caption   : "
    f"{final_row['generated_caption']}"
)

print(
    f"Generated Image     : "
    f"{final_row['generated_image_path']}"
)


# ============================================
# FINAL TEST
# ============================================

if (
    final_row["verification_status"]
    == "FACT_CHECKED"
    and
    final_row["approval_status"]
    == "WAITING_APPROVAL"
    and
    final_row["generated_title"]
    and
    final_row["generated_caption"]
    and
    final_row["generated_image_path"]
):

    print("\n========================================")
    print("FULL PIPELINE TEST PASSED!")
    print("========================================")

    print(
        "\nThe post successfully completed:"
    )

    print(
        "1. Fact extraction"
    )

    print(
        "2. Instagram content generation"
    )

    print(
        "3. Generated-content verification"
    )

    print(
        "4. FLUX AI image generation"
    )

    print(
        "5. Image path database storage"
    )

    print(
        "6. Human approval queue"
    )

else:

    print("\n========================================")
    print("FULL PIPELINE TEST FAILED")
    print("========================================")
