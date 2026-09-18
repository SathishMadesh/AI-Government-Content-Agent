from backend.app.database import get_connection
from backend.app.services.content_service import (
    update_verification_status,
    send_for_approval
)


SOURCE_POST_ID = "2311294"


# ============================================
# GET CURRENT RECORD
# ============================================

connection = get_connection()

row = connection.execute("""
    SELECT
        source_post_id,
        source_title,
        verification_status,
        approval_status,
        generated_image_path
    FROM content_items
    WHERE source_post_id = ?
""", (SOURCE_POST_ID,)).fetchone()

connection.close()


if not row:

    print("\nRecord not found.")

    raise SystemExit


print("\n========================================")
print("CURRENT RECORD")
print("========================================")

print(
    f"Source Post ID       : {row['source_post_id']}"
)

print(
    f"Source Title         : {row['source_title']}"
)

print(
    f"Verification Status  : {row['verification_status']}"
)

print(
    f"Approval Status      : {row['approval_status']}"
)

print(
    f"Generated Image      : {row['generated_image_path']}"
)


# ============================================
# MARK CONTENT AS FACT CHECKED
# ============================================

print("\n========================================")
print("FACT CHECK STATUS")
print("========================================")

print(
    "\nMarking content as FACT_CHECKED..."
)

update_verification_status(
    SOURCE_POST_ID,
    "FACT_CHECKED"
)


# ============================================
# SEND FOR HUMAN APPROVAL
# ============================================

print("\n========================================")
print("APPROVAL")
print("========================================")

print(
    "\nSending post for human approval..."
)

send_for_approval(
    SOURCE_POST_ID
)


# ============================================
# GET UPDATED RECORD
# ============================================

connection = get_connection()

row = connection.execute("""
    SELECT
        source_post_id,
        source_title,
        verification_status,
        approval_status,
        generated_image_path
    FROM content_items
    WHERE source_post_id = ?
""", (SOURCE_POST_ID,)).fetchone()

connection.close()


# ============================================
# DISPLAY FINAL STATUS
# ============================================

print("\n========================================")
print("FINAL STATUS")
print("========================================")

print(
    f"Source Post ID       : {row['source_post_id']}"
)

print(
    f"Source Title         : {row['source_title']}"
)

print(
    f"Verification Status  : {row['verification_status']}"
)

print(
    f"Approval Status      : {row['approval_status']}"
)

print(
    f"Generated Image      : {row['generated_image_path']}"
)


# ============================================
# VERIFY WORKFLOW
# ============================================

if (
    row["verification_status"] == "FACT_CHECKED"
    and
    row["approval_status"] == "WAITING_APPROVAL"
):

    print("\n========================================")
    print("SUCCESS!")
    print("========================================")

    print(
        "\nContent is fact-checked and waiting "
        "for human approval."
    )

else:

    print("\n========================================")
    print("ERROR")
    print("========================================")

    print(
        "\nApproval workflow failed."
    )

