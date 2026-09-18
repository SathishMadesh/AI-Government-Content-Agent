import json

from backend.app.database import get_connection
from backend.app.collectors.pib_pmo import get_pmo_releases, get_release_details, parse_pib_date
from backend.app.services.content_detector import is_new_content
from backend.app.services.fact_extractor import extract_facts

from datetime import datetime, timedelta
from backend.app.services.relevance_detector import (
    check_relevance
)

from backend.app.services.image_strategy import choose_image_strategy
from backend.app.services.visual_concept_generator import generate_visual_concept
from backend.app.services.image_generator import (
    generate_ai_background,
    generate_instagram_image
)

from backend.app.services.content_generator import (
    generate_instagram_content
)

from backend.app.services.generated_content_verifier import (
    verify_generated_content
)

def get_existing_ids():
    connection = get_connection()

    rows = connection.execute("""
        SELECT source_post_id
        FROM content_items
    """).fetchall()

    connection.close()

    return [row["source_post_id"] for row in rows]


def save_release(release):
    connection = get_connection()

    connection.execute("""
        INSERT INTO content_items (
            source,
            source_post_id,
            source_url,
            source_date,
            source_title,
            source_text,
            verification_status,
            approval_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        release["source"],
        release["source_post_id"],
        release["source_url"],
        release["source_date"],
        release["source_title"],
        release["source_text"],
        "NEW",
        "PENDING"
    ))

    connection.commit()
    connection.close()

def save_extracted_facts(source_post_id, facts):
    connection = get_connection()

    connection.execute("""
        UPDATE content_items
        SET
            extracted_facts = ?,
            verification_status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE source_post_id = ?
    """, (
        json.dumps(facts),
        "FACTS_EXTRACTED",
        source_post_id
    ))

    connection.commit()
    connection.close()

def update_verification_status(source_post_id, status):
    connection = get_connection()

    connection.execute("""
        UPDATE content_items
        SET
            verification_status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE source_post_id = ?
    """, (
        status,
        source_post_id
    ))

    connection.commit()
    connection.close()

def collect_new_releases():

    print("\nStarting official news collection...\n")

    releases = get_pmo_releases()

    existing_ids = set(get_existing_ids())

    new_count = 0
    high_priority_count = 0
    low_priority_count = 0
    not_relevant_count = 0

    for index, release in enumerate(
        releases,
        start=1
    ):

        release_id = release["release_id"]

        print(
            f"\nChecking listing {index}/{len(releases)}"
        )

        print(
            f"Release ID: {release_id}"
        )

        # --------------------------------
        # SKIP ALREADY PROCESSED RELEASES
        # --------------------------------

        if release_id in existing_ids:

            print(
                "Already processed - skipping."
            )

            continue

        try:

            # --------------------------------
            # GET FULL RELEASE DETAILS
            # --------------------------------

            details = get_release_details(
                release["url"]
            )

            release_data = {
                "source": "PIB",
                "source_post_id": details[
                    "source_post_id"
                ],
                "source_url": details[
                    "source_url"
                ],
                "source_date": details[
                    "source_date"
                ],
                "source_title": release[
                    "title"
                ],
                "source_text": details[
                    "source_text"
                ]
            }

            # --------------------------------
            # SAVE RELEASE
            # --------------------------------

            save_release(
                release_data
            )

            existing_ids.add(
                release_id
            )

            new_count += 1

            print(
                "\nNew release saved."
            )

            # --------------------------------
            # RELEVANCE CHECK
            # --------------------------------

            print(
                "\nChecking relevance..."
            )

            relevance_result = check_relevance(
                release_data["source_title"],
                release_data["source_text"]
            )

            print(
                f"Relevance result: "
                f"{relevance_result}"
            )

            save_relevance_result(
                release_data["source_post_id"],
                relevance_result
            )

            priority = relevance_result.get(
                "priority",
                "LOW_PRIORITY"
            )

            # --------------------------------
            # NOT RELEVANT
            # --------------------------------

            if priority == "NOT_RELEVANT":

                not_relevant_count += 1

                print(
                    "\nSkipped: Not relevant"
                )

                continue

            # --------------------------------
            # LOW PRIORITY
            # --------------------------------

            if priority == "LOW_PRIORITY":

                low_priority_count += 1

                print(
                    "\nSkipped: Low priority news"
                )

                continue

            # --------------------------------
            # HIGH PRIORITY
            # --------------------------------

            if priority == "HIGH_PRIORITY":

                high_priority_count += 1

                print(
                    "\nHigh priority news found!"
                )

                # --------------------------------
                # EXTRACT FACTS
                # --------------------------------

                print(
                    "\nExtracting verified facts..."
                )

                facts = extract_facts(
                    release_data["source_text"]
                )

                save_extracted_facts(
                    release_data["source_post_id"],
                    facts
                )

                print(
                    "\nFacts extracted successfully."
                )

                # --------------------------------
                # GENERATE INSTAGRAM CONTENT
                # --------------------------------

                print(
                    "\nGenerating Instagram content..."
                )

                generated_content = (
                    generate_instagram_content(
                        source_text=release_data[
                            "source_text"
                        ],
                        facts=facts
                    )
                )

                if not generated_content:

                    print(
                        "\nContent generation failed."
                    )

                    update_verification_status(
                        release_data[
                            "source_post_id"
                        ],
                        "FAILED"
                    )

                    continue

                print(
                    "\nInstagram content generated."
                )

                print(
                    f"Title: "
                    f"{generated_content.get('title', '')}"
                )

                # --------------------------------
                # VERIFY GENERATED CONTENT
                # --------------------------------

                print(
                    "\nVerifying generated content..."
                )

                verification_result = (
                    verify_generated_content(
                        generated_content,
                        release_data["source_text"],
                        facts
                    )
                )

                print("\nGenerated content verification:")
                print(verification_result)

                save_generated_content(
                    release_data["source_post_id"],
                    generated_content
                )

                if verification_result.get("verified"):

                    update_verification_status(
                        release_data["source_post_id"],
                        "FACT_CHECKED"
                    )

                else:

                    update_verification_status(
                        release_data["source_post_id"],
                        "FACT_CHECK_FAILED"
                    )

                # --------------------------------
                # CHECK VERIFICATION RESULT
                # --------------------------------

                if verification_result.get(
                    "verified"
                ):

                    print(
                        "\nGenerated content PASSED verification."
                    )

                    # --------------------------------
                    # GENERATE IMAGE
                    # --------------------------------

                    final_image = (
                        generate_content_image(
                            source_post_id=
                                release_data[
                                    "source_post_id"
                                ],
                            source_url=
                                release_data[
                                    "source_url"
                                ],
                            source_title=
                                release_data[
                                    "source_title"
                                ],
                            source_text=
                                release_data[
                                    "source_text"
                                ],
                            facts=facts
                        )
                    )

                    if not final_image:

                        print(
                            "\nImage generation failed."
                        )

                        update_verification_status(
                            release_data[
                                "source_post_id"
                            ],
                            "FAILED"
                        )

                        continue

                    print(
                        "\nInstagram image generated successfully."
                    )

                    # --------------------------------
                    # SEND FOR HUMAN APPROVAL
                    # --------------------------------

                    send_for_approval(
                        release_data[
                            "source_post_id"
                        ]
                    )

                    print(
                        "\nPost sent for human approval."
                    )

                else:

                    print(
                        "\nGenerated content FAILED verification."
                    )

                    update_verification_status(
                        release_data[
                            "source_post_id"
                        ],
                        "FACT_CHECK_FAILED"
                    )

        except Exception as error:

            print(
                f"\nError processing "
                f"{release_id}: {error}"
            )

            # --------------------------------
            # MARK FAILED
            # --------------------------------

            try:

                update_verification_status(
                    release_id,
                    "FAILED"
                )

            except Exception:

                pass

    # --------------------------------
    # FINAL SUMMARY
    # --------------------------------

    print(
        "\n--- COLLECTION COMPLETE ---"
    )

    print(
        f"New releases: {new_count}"
    )

    print(
        f"High priority: {high_priority_count}"
    )

    print(
        f"Low priority: {low_priority_count}"
    )

    print(
        f"Not relevant: {not_relevant_count}"
    )

def save_generated_content(source_post_id, generated_content):
    connection = get_connection()

    connection.execute("""
        UPDATE content_items
        SET
            generated_title = ?,
            generated_caption = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE source_post_id = ?
    """, (
        generated_content["title"],
        generated_content["caption"],
        source_post_id
    ))

    connection.commit()
    connection.close()

def generate_content_image(
    source_post_id,
    source_url,
    source_title,
    source_text,
    facts
):

    print("\n--- IMAGE GENERATION STARTED ---")

    # --------------------------------
    # CHECK OFFICIAL IMAGE
    # --------------------------------

    strategy_result = choose_image_strategy(
        source_url
    )

    strategy = strategy_result["strategy"]

    # --------------------------------
    # OFFICIAL IMAGE
    # --------------------------------

    if strategy == "OFFICIAL_IMAGE":

        image_source = strategy_result[
            "image"
        ]["url"]

        print("\nUsing official PIB image.")

    # --------------------------------
    # AI GENERATED IMAGE
    # --------------------------------

    else:

        print(
            "\nNo suitable official image."
        )

        print(
            "Generating visual concept..."
        )

        visual_concept = generate_visual_concept(
            title=source_title,
            source_text=source_text,
            facts=facts
        )

        if not visual_concept:

            print(
                "Visual concept generation failed."
            )

            return None

        image_prompt = visual_concept.get(
            "image_prompt"
        )

        if not image_prompt:

            print(
                "No image prompt generated."
            )

            return None

        image_source = generate_ai_background(
            image_prompt,
            source_post_id
        )

        if not image_source:

            print(
                "AI image generation failed."
            )

            return None

    # --------------------------------
    # CREATE FINAL INSTAGRAM IMAGE
    # --------------------------------

    final_image = generate_instagram_image(
        title=source_title,
        image_source=image_source,
        source="PIB",
        source_post_id=source_post_id
    )

    # --------------------------------
    # SAVE IMAGE PATH
    # --------------------------------

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
            source_post_id
        ))

        connection.commit()
        connection.close()

        print(
            "\nImage path saved to database:"
        )

        print(final_image)

    return final_image

def save_relevance_result(
    source_post_id,
    relevance_result
):

    connection = get_connection()

    priority = relevance_result.get(
        "priority",
        "LOW_PRIORITY"
    )

    connection.execute("""
        UPDATE content_items
        SET
            verification_status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE source_post_id = ?
    """, (
        priority,
        source_post_id
    ))

    connection.commit()
    connection.close()


def send_for_approval(source_post_id):
    connection = get_connection()

    connection.execute("""
        UPDATE content_items
        SET
            approval_status = 'WAITING_APPROVAL',
            updated_at = CURRENT_TIMESTAMP
        WHERE source_post_id = ?
          AND verification_status = 'FACT_CHECKED'
    """, (source_post_id,))

    connection.commit()
    connection.close()


def update_approval_status(source_post_id, status):
    connection = get_connection()

    connection.execute("""
        UPDATE content_items
        SET
            approval_status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE source_post_id = ?
    """, (status, source_post_id))

    connection.commit()
    connection.close()

if __name__ == "__main__":
    collect_new_releases()