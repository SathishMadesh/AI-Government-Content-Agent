import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from datetime import datetime, timedelta
import re

from zoneinfo import ZoneInfo

PIB_PMO_URL = "https://www.pib.gov.in/AllRelease.aspx?MenuId=23&PMO=1&lang=1&reg=1"
PIB_BASE_URL = "https://www.pib.gov.in"


def get_pmo_releases():

    response = httpx.get(
        PIB_PMO_URL,
        timeout=30,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    releases = []
    seen_ids = set()

    # Find the PMO section heading
    pmo_heading = None

    for heading in soup.find_all("h3"):

        heading_text = heading.get_text(
            " ",
            strip=True
        )

        if heading_text.lower() == "prime minister's office":

            pmo_heading = heading
            break

    if not pmo_heading:

        print(
            "Prime Minister's Office section not found."
        )

        return []

    print(
        "\nPrime Minister's Office section found."
    )

    # Walk through elements after the PMO heading
    for element in pmo_heading.find_all_next():

        # Stop when the next section starts
        if element.name == "h3":

            break

        # Only process release list items
        if element.name != "li":
            continue

        link = element.find(
            "a",
            href=True
        )

        if not link:
            continue

        href = link["href"]

        if "PRID=" not in href:
            continue

        title = link.get_text(
            " ",
            strip=True
        )

        if not title:
            continue

        full_url = urljoin(
            PIB_BASE_URL,
            href
        )

        release_id = (
            full_url
            .split("PRID=")[-1]
            .split("&")[0]
        )

        if release_id in seen_ids:
            continue

        seen_ids.add(release_id)

        # Extract posted date directly from the same <li>
        date_element = element.find(
            "span",
            class_="publishdatesmall"
        )

        posted_date = ""

        if date_element:

            posted_date = date_element.get_text(
                " ",
                strip=True
            )

            posted_date = re.sub(
                r"^Posted\s*on:\s*",
                "",
                posted_date,
                flags=re.IGNORECASE
            ).strip()

        # --------------------------------
        # ONLY KEEP TODAY'S RELEASES
        # --------------------------------

        parsed_date = parse_pib_date(posted_date)

        if parsed_date is None:
            continue

        india_today = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).date()

        if parsed_date.date() != india_today:
            continue

        releases.append({
            "release_id": release_id,
            "title": title,
            "url": full_url,
            "posted_date": posted_date
        })

    print(
        f"\nPMO releases found: {len(releases)}"
    )

    return releases

def get_release_details(url):
    prid = url.split("PRID=")[-1].split("&")[0]

    english_url = (
        f"https://www.pib.gov.in/"
        f"PressReleasePage.aspx?PRID={prid}&lang=1&reg=3"
    )

    response = httpx.get(
        english_url,
        timeout=30,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Get page title
    page_title = soup.title.get_text(strip=True) if soup.title else ""

    # Get all visible text
    text = soup.get_text("\n", strip=True)

    # Find release title
    title = ""
    title_element = soup.find(
        string=lambda s: s and "Prime Minister congratulates" in s
    )

    if title_element:
        title = title_element.strip()

    # Find posted date
    posted_on = ""
    posted_element = soup.find(
        string=lambda s: s and "Posted On:" in s
    )

    if posted_element:
        parent_text = posted_element.parent.get_text(" ", strip=True)
        posted_on = parent_text.replace("Posted On:", "").strip()

    # Remove repeated navigation/footer content
    end_marker = "*****"

    if title and title in text:
        text = text.split(title, 1)[1]

    if end_marker in text:
        text = text.split(end_marker, 1)[0]

    text = text.strip()

    return {
        "source": "PIB",
        "source_post_id": prid,
        "source_url": str(response.url),
        "source_title": title,
        "source_date": posted_on,
        "source_text": text,
        "page_title": page_title
    }

def is_pmo_release(url):

    try:

        response = httpx.get(
            url,
            timeout=30,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        text = soup.get_text(
            " ",
            strip=True
        )

        return "Prime Minister's Office" in text

    except Exception as error:

        print(
            f"Could not validate release: {url}"
        )

        print(error)

        return False

def parse_pib_date(date_text):

    if not date_text:
        return None

    clean_date = re.sub(
        r"\s+by\s+PIB.*$",
        "",
        date_text,
        flags=re.IGNORECASE
    ).strip()

    # Format 1:
    # 08 SEP 2026 7:51PM
    try:
        return datetime.strptime(
            clean_date,
            "%d %b %Y %I:%M%p"
        )

    except ValueError:
        pass

    # Format 2:
    # 01 Sep 2026
    try:
        return datetime.strptime(
            clean_date,
            "%d %b %Y"
        )

    except ValueError as error:

        print(
            f"Could not parse date: {date_text}"
        )

        print(error)

        return None



if __name__ == "__main__":

    releases = get_pmo_releases()

    print(
        f"\nTotal releases found: {len(releases)}"
    )

    # Last 2 days
    cutoff_date = datetime.now() - timedelta(days=2)

    print(
        f"\nCollecting releases after: "
        f"{cutoff_date.strftime('%d %b %Y %I:%M %p')}"
    )

    print(
        "\n--- RECENT RELEASES ---\n"
    )

    recent_count = 0

    recent_releases = []

    for release in releases:

        try:

            details = get_release_details(
                release["url"]
            )

            release_date = parse_pib_date(
                details["source_date"]
            )

            if (
                release_date
                and release_date >= cutoff_date
            ):

                details["parsed_date"] = release_date

                # Use listing title for now
                details["source_title"] = release["title"]

                recent_releases.append(details)

        except Exception as error:

            print(
                f"Error processing release: {error}"
            )
            
    recent_releases.sort(
        key=lambda item: item["parsed_date"],
        reverse=True
    )

    print("\n--- RECENT RELEASES ---\n")

    for release in recent_releases:

        print(
            f"Release ID: "
            f"{release['source_post_id']}"
        )

        print(
            f"Date: "
            f"{release['source_date']}"
        )

        print(
            f"Title: "
            f"{release['source_title']}"
        )

        print("-" * 80)

    print(
        f"\nRecent releases found: "
        f"{len(recent_releases)}"
    )