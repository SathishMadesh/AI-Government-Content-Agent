from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

from backend.app.database import get_connection
from backend.app.services.content_service import (
    update_approval_status,
    collect_new_releases
)

from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.app.services.instagram_service import (
    publish_to_instagram,
    INSTAGRAM_PUBLISH_ENABLED
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    print("APScheduler started — checking PIB every hour.")

    yield

    scheduler.shutdown()
    print("APScheduler stopped.")

app = FastAPI(
    title="AI Government Content Repurposing Agent",
    description="AI agent for creating verified Instagram content from authoritative government sources.",
    version="1.0.0",
    lifespan=lifespan
)

scheduler = BackgroundScheduler()

scheduler.add_job(
    collect_new_releases,
    "interval",
    hours=1,
    id="pib_collection_job",
    replace_existing=True
)



GENERATED_IMAGES_DIR = Path("generated_images")

GENERATED_IMAGES_DIR.mkdir(
    exist_ok=True
)

app.mount(
    "/generated-images",
    StaticFiles(directory=str(GENERATED_IMAGES_DIR)),
    name="generated-images"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "running",
        "message": "AI Government Content Repurposing Agent API is running"
    }


@app.get("/approval/pending")
def get_pending_content():
    connection = get_connection()

    rows = connection.execute("""
        SELECT
            id,
            source,
            source_post_id,
            source_url,
            source_date,
            source_title,
            source_text,
            extracted_facts,
            generated_title,
            generated_caption,
            generated_image_path,
            verification_status,
            approval_status
        FROM content_items
        WHERE verification_status = 'FACT_CHECKED'
          AND approval_status = 'WAITING_APPROVAL'
        ORDER BY created_at DESC
    """).fetchall()

    connection.close()

    results = []

    for row in rows:
        item = dict(row)

        if item["generated_image_path"]:
            filename = Path(
                item["generated_image_path"]
            ).name

            item["generated_image_url"] = (
                f"/generated-images/{filename}"
            )
        else:
            item["generated_image_url"] = None

        if item["extracted_facts"]:
            import json
            item["extracted_facts"] = json.loads(
                item["extracted_facts"]
            )

        results.append(item)

    return results


@app.post("/approval/{source_post_id}/approve")
def approve_content(source_post_id: str):

    connection = get_connection()

    row = connection.execute("""
        SELECT *
        FROM content_items
        WHERE source_post_id = ?
    """, (source_post_id,)).fetchone()

    connection.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Content not found"
        )

    # Prevent duplicate publishing
    if row["publish_status"] == "PUBLISHED":
        return {
            "status": "ALREADY_PUBLISHED",
            "source_post_id": source_post_id,
            "instagram_post_id": row["instagram_post_id"]
        }

    # Extra duplicate protection
    if row["instagram_post_id"]:
        return {
            "status": "ALREADY_PUBLISHED",
            "source_post_id": source_post_id,
            "instagram_post_id": row["instagram_post_id"]
        }

    if row["publish_status"] == "PUBLISHING":
        return {
            "status": "ALREADY_PUBLISHING",
            "source_post_id": source_post_id,
            "message": "This content is currently being published"
        }

    # Fact-check protection
    if row["verification_status"] != "FACT_CHECKED":
        raise HTTPException(
            status_code=400,
            detail="Content has not passed fact checking"
        )

    # Approval protection
    if row["approval_status"] != "WAITING_APPROVAL":
        raise HTTPException(
            status_code=400,
            detail="Content is not waiting for approval"
        )

    # Check generated image
    image_path = row["generated_image_path"]

    if not image_path:

        connection = get_connection()

        connection.execute("""
            UPDATE content_items
            SET
                publish_status = ?,
                publish_error = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE source_post_id = ?
        """, (
            "PUBLISH_FAILED",
            "Generated image not found",
            source_post_id
        ))

        connection.commit()
        connection.close()

        return {
            "status": "APPROVED",
            "publish_status": "PUBLISH_FAILED",
            "error": "Generated image not found"
        }

    # Mark content as approved
    update_approval_status(
        source_post_id,
        "APPROVED"
    )

    # --------------------------------------------------
    # SAFE MODE
    # Instagram publishing is disabled
    # --------------------------------------------------

    if not INSTAGRAM_PUBLISH_ENABLED:

        connection = get_connection()

        connection.execute("""
            UPDATE content_items
            SET
                publish_status = ?,
                publish_error = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE source_post_id = ?
        """, (
            "APPROVED",
            source_post_id
        ))

        connection.commit()
        connection.close()

        return {
            "status": "APPROVED",
            "publish_status": "NOT_PUBLISHED",
            "source_post_id": source_post_id,
            "message": "Content approved. Instagram publishing is currently disabled."
        }

    # --------------------------------------------------
    # INSTAGRAM PUBLISHING
    # Only reached when publishing is enabled
    # --------------------------------------------------

    connection = get_connection()

    connection.execute("""
        UPDATE content_items
        SET
            publish_status = ?,
            publish_error = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE source_post_id = ?
    """, (
        "PUBLISHING",
        source_post_id
    ))

    connection.commit()
    connection.close()

    # Publish to Instagram
    result = publish_to_instagram(
        image_path,
        row["generated_caption"]
    )

    connection = get_connection()

    if result["success"]:

        connection.execute("""
            UPDATE content_items
            SET
                instagram_post_id = ?,
                publish_status = ?,
                publish_error = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE source_post_id = ?
        """, (
            result["instagram_post_id"],
            "PUBLISHED",
            source_post_id
        ))

        connection.commit()
        connection.close()

        return {
            "status": "PUBLISHED",
            "source_post_id": source_post_id,
            "instagram_post_id": result["instagram_post_id"]
        }

    else:

        connection.execute("""
            UPDATE content_items
            SET
                publish_status = ?,
                publish_error = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE source_post_id = ?
        """, (
            "PUBLISH_FAILED",
            result["error"],
            source_post_id
        ))

        connection.commit()
        connection.close()

        return {
            "status": "APPROVED",
            "publish_status": "PUBLISH_FAILED",
            "error": result["error"]
        }


@app.post("/approval/{source_post_id}/reject")
def reject_content(source_post_id: str):

    connection = get_connection()

    row = connection.execute("""
        SELECT *
        FROM content_items
        WHERE source_post_id = ?
    """, (source_post_id,)).fetchone()

    connection.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Content not found"
        )

    if row["approval_status"] != "WAITING_APPROVAL":
        raise HTTPException(
            status_code=400,
            detail="Content is not waiting for approval"
        )

    update_approval_status(
        source_post_id,
        "REJECTED"
    )

    return {
        "status": "REJECTED",
        "source_post_id": source_post_id
    }