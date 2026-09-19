import os
import io
import textwrap
import httpx
import base64
import requests

from dotenv import load_dotenv

from backend.app.services.visual_concept_generator import generate_visual_concept
from backend.app.services.image_strategy import choose_image_strategy

load_dotenv()

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

CLOUDFLARE_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageEnhance,
    ImageFilter
)


OUTPUT_FOLDER = "generated_images"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


def get_font(
    size,
    bold=False
):

    if os.name == "nt":

        if bold:

            font_path = (
                "C:/Windows/Fonts/arialbd.ttf"
            )

        else:

            font_path = (
                "C:/Windows/Fonts/arial.ttf"
            )

    else:

        if bold:

            font_path = (
                "/usr/share/fonts/truetype/dejavu/"
                "DejaVuSans-Bold.ttf"
            )

        else:

            font_path = (
                "/usr/share/fonts/truetype/dejavu/"
                "DejaVuSans.ttf"
            )

    return ImageFont.truetype(
        font_path,
        size
    )


def load_background_image(
    image_source
):

    try:

        # -------------------------
        # URL IMAGE
        # -------------------------

        if image_source.startswith(
            "http"
        ):

            response = httpx.get(
                image_source,
                timeout=30,
                follow_redirects=True
            )

            response.raise_for_status()

            image = Image.open(
                io.BytesIO(
                    response.content
                )
            )

        # -------------------------
        # LOCAL IMAGE
        # -------------------------

        else:

            image = Image.open(
                image_source
            )

        return image.convert(
            "RGB"
        )

    except Exception as error:

        print(
            "\nError loading background image:"
        )

        print(
            error
        )

        return None


def create_background(
    image,
    width,
    height
):

    # Resize image to cover
    # Instagram portrait format

    image_ratio = (
        image.width / image.height
    )

    target_ratio = (
        width / height
    )

    if image_ratio > target_ratio:

        # Image is wider
        new_height = height

        new_width = int(
            new_height * image_ratio
        )

    else:

        # Image is taller
        new_width = width

        new_height = int(
            new_width / image_ratio
        )

    image = image.resize(
        (
            new_width,
            new_height
        ),
        Image.LANCZOS
    )

    # Center crop

    left = (
        new_width - width
    ) // 2

    top = (
        new_height - height
    ) // 2

    image = image.crop(
        (
            left,
            top,
            left + width,
            top + height
        )
    )

    return image


def add_dark_overlay(
    image
):

    overlay = Image.new(
        "RGBA",
        image.size,
        (
            0,
            0,
            0,
            120
        )
    )

    image = image.convert(
        "RGBA"
    )

    image = Image.alpha_composite(
        image,
        overlay
    )

    return image

def generate_ai_background(image_prompt, source_post_id):

    print("\nGenerating AI background image...")

    if not CLOUDFLARE_ACCOUNT_ID:
        print("CLOUDFLARE_ACCOUNT_ID not found in .env")
        return None

    if not CLOUDFLARE_API_TOKEN:
        print("CLOUDFLARE_API_TOKEN not found in .env")
        return None

    try:

        url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{CLOUDFLARE_ACCOUNT_ID}/ai/run/"
            f"{CLOUDFLARE_IMAGE_MODEL}"
        )

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": image_prompt
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        image_base64 = (
            result
            .get("result", {})
            .get("image")
        )

        if not image_base64:
            print("\nCloudflare returned no image.")
            return None

        image_data = base64.b64decode(
            image_base64
        )

        output_path = os.path.join(
            OUTPUT_FOLDER,
            f"{source_post_id}_background.png"
        )

        with open(
            output_path,
            "wb"
        ) as image_file:

            image_file.write(
                image_data
            )

        print(
            "\nAI background created:"
        )

        print(
            output_path
        )

        return output_path

    except Exception as error:

        print(
            "\nError generating AI background:"
        )

        print(error)

        return None

def generate_instagram_image(
    title,
    image_source,
    source,
    source_post_id
):

    print(
        "\nGenerating Instagram post..."
    )

    # -------------------------
    # INSTAGRAM SIZE
    # -------------------------

    width = 1080
    height = 1350

    # -------------------------
    # LOAD BACKGROUND
    # -------------------------

    background = load_background_image(
        image_source
    )

    if not background:

        print(
            "\nUsing fallback background..."
        )

        background = Image.new(
            "RGB",
            (
                width,
                height
            ),
            (
                30,
                30,
                30
            )
        )

    else:

        background = create_background(
            background,
            width,
            height
        )

    # -------------------------
    # DARK OVERLAY
    # -------------------------

    image = add_dark_overlay(
        background
    )

    draw = ImageDraw.Draw(
        image
    )

    # -------------------------
    # FONTS
    # -------------------------

    label_font = get_font(
        32,
        bold=True
    )

    title_font = get_font(
        64,
        bold=True
    )

    footer_font = get_font(
        27
    )

    # -------------------------
    # TOP LABEL
    # -------------------------

    label = "OFFICIAL UPDATE"

    draw.text(
        (
            70,
            70
        ),
        label,
        font=label_font,
        fill="white"
    )

    # -------------------------
    # SMALL DIVIDER
    # -------------------------

    draw.rectangle(
        (
            70,
            125,
            260,
            132
        ),
        fill="white"
    )

    # -------------------------
    # TITLE
    # -------------------------

    wrapped_title = textwrap.wrap(
        title,
        width=26
    )

    y_position = 820

    for line in wrapped_title:

        draw.text(
            (
                70,
                y_position
            ),
            line,
            font=title_font,
            fill="white"
        )

        y_position += 78

    # -------------------------
    # SOURCE AREA
    # -------------------------

    draw.rectangle(
        (
            70,
            1190,
            1010,
            1193
        ),
        fill="white"
    )

    footer = (
        f"Source: {source}"
    )

    draw.text(
        (
            70,
            1215
        ),
        footer,
        font=footer_font,
        fill="white"
    )

    # -------------------------
    # SAVE
    # -------------------------

    output_path = os.path.join(
        OUTPUT_FOLDER,
        f"{source_post_id}_instagram_post.jpg"
    )

    image.convert(
        "RGB"
    ).save(
        output_path,
        quality=95
    )

    print(
        "\nInstagram image created:"
    )

    print(
        output_path
    )

    return output_path


if __name__ == "__main__":

    title = (
        "Cabinet approves major "
        "railway expansion projects"
    )

    source_text = """
    The Cabinet has approved major railway
    expansion projects to improve connectivity
    and infrastructure across several regions.
    """

    facts = {
        "category": "Infrastructure",
        "topic": "Railway expansion",
        "source": "PIB"
    }

    source_url = (
        "https://www.pib.gov.in/"
        "PressReleasePage.aspx?PRID=2306668"
    )

    print("\nChecking image strategy...")

    strategy_result = choose_image_strategy(
        source_url
    )

    strategy = strategy_result.get(
        "strategy"
    )

    selected_image = None

    # --------------------------------
    # OFFICIAL IMAGE
    # --------------------------------

    if strategy == "OFFICIAL_IMAGE":

        print(
            "\nUsing official PIB image."
        )

        official_image = strategy_result.get(
            "image"
        )

        if official_image:

            selected_image = official_image.get(
                "url"
            )

    # --------------------------------
    # GENERATED VISUAL
    # --------------------------------

    elif strategy == "GENERATED_VISUAL":

        print(
            "\nNo suitable official image."
        )

        print(
            "Generating visual concept..."
        )

        visual_concept = generate_visual_concept(
            title=title,
            source_text=source_text,
            facts=facts
        )

        if visual_concept:

            print(
                "\nVisual concept generated:"
            )

            print(
                visual_concept
            )

            image_prompt = visual_concept.get(
                "image_prompt"
            )

            if image_prompt:

                selected_image = generate_ai_background(
                    image_prompt
                )

    # --------------------------------
    # GENERATE INSTAGRAM POST
    # --------------------------------

    if selected_image:

        generate_instagram_image(
            title=title,
            image_source=selected_image,
            source="PIB"
        )

    else:

        print(
            "\nNo image available."
        )