import sqlite3

DATABASE_PATH = "database/content_agent.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
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

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")