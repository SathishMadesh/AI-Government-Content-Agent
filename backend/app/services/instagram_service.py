import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")
INSTAGRAM_PUBLISH_ENABLED = (
    os.getenv("INSTAGRAM_PUBLISH_ENABLED", "false").lower()
    == "true"
)

BASE_URL = "https://graph.instagram.com"


def check_instagram_connection():

    url = f"{BASE_URL}/me"

    params = {
        "fields": "id,username,account_type",
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }

    response = requests.get(url, params=params)

    print("Status Code:", response.status_code)
    print("Response:", response.json())


def create_media_container(image_url, caption):

    url = f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media"

    data = {
        "image_url": image_url,
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }

    response = requests.post(url, data=data)

    print("Create Container Status:", response.status_code)
    print("Response:", response.json())

    return response.json()

def check_media_status(container_id):

    url = f"{BASE_URL}/{container_id}"

    params = {
        "fields": "status_code,status",
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }

    response = requests.get(url, params=params)

    print("Media Status Check:", response.status_code)
    print("Response:", response.json())

    return response.json()

def publish_media(container_id):

    url = f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media_publish"

    data = {
        "creation_id": container_id,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }

    response = requests.post(url, data=data)

    print("Publish Status:", response.status_code)
    print("Response:", response.json())

    return response.json()


def publish_to_instagram(image_path, caption):

    if not INSTAGRAM_PUBLISH_ENABLED:

        print("\nInstagram publishing is DISABLED.")
        print("Approval recorded, but nothing was published.")

        return {
            "success": False,
            "error": "Instagram publishing is disabled."
        }

    # Convert local generated image path to public URL
    filename = os.path.basename(image_path)

    image_url = (
        f"{PUBLIC_BASE_URL}"
        f"/generated-images/{filename}"
    )

    print("\nInstagram Image URL:")
    print(image_url)

    # Step 1: Create media container
    container_response = create_media_container(
        image_url,
        caption
    )

    if "id" not in container_response:

        error = container_response.get(
            "error",
            container_response
        )

        return {
            "success": False,
            "error": str(error)
        }

    container_id = container_response["id"]

    print("\nMedia Container Created:")
    print(container_id)

    # Step 2: Wait for Instagram to finish processing
    max_attempts = 6

    for attempt in range(max_attempts):

        status_response = check_media_status(
            container_id
        )

        status_code = status_response.get("status_code")

        print(
            f"Media processing status "
            f"({attempt + 1}/{max_attempts}): "
            f"{status_code}"
        )

        if status_code == "FINISHED":
            break

        if status_code == "ERROR":
            return {
                "success": False,
                "error": str(status_response)
            }

        if attempt < max_attempts - 1:
            time.sleep(5)

    else:
        return {
            "success": False,
            "error": "Instagram media was not ready after waiting."
        }

    # Step 3: Publish media
    publish_response = publish_media(
        container_id
    )

    if "id" not in publish_response:

        error = publish_response.get(
            "error",
            publish_response
        )

        return {
            "success": False,
            "error": str(error)
        }

    instagram_post_id = publish_response["id"]

    print("\nInstagram Post Published:")
    print(instagram_post_id)

    return {
        "success": True,
        "instagram_post_id": instagram_post_id
    }