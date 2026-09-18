from backend.app.database import get_connection


connection = get_connection()

rows = connection.execute("""
    SELECT
        source_post_id,
        source_title,
        verification_status,
        approval_status
    FROM content_items
    WHERE verification_status = 'FACTS_EXTRACTED'
    LIMIT 5
""").fetchall()

connection.close()


print("\nFACTS_EXTRACTED records:\n")

for row in rows:
    print(dict(row))