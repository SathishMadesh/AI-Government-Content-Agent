import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "content_agent.db"


def get_connection():
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS content_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_post_id TEXT NOT NULL,
            source_url TEXT NOT NULL,
            source_date TEXT,
            source_title TEXT,
            source_text TEXT,
            extracted_facts TEXT,
            verification_status TEXT DEFAULT 'NEW',
            generated_caption TEXT,
            generated_title TEXT,
            generated_image_path TEXT,
            approval_status TEXT DEFAULT 'PENDING',
            instagram_post_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source, source_post_id)
        )
    """)

    # Add publishing columns if they do not already exist
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(content_items)").fetchall()
    }

    if "publish_status" not in columns:
        connection.execute("""
            ALTER TABLE content_items
            ADD COLUMN publish_status TEXT DEFAULT 'NOT_PUBLISHED'
        """)

    if "publish_error" not in columns:
        connection.execute("""
            ALTER TABLE content_items
            ADD COLUMN publish_error TEXT
        """)

    connection.commit()
    connection.close()



if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")