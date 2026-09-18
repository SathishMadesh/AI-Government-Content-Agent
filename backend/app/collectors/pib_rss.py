import httpx
import xml.etree.ElementTree as ET


PIB_RSS_URL = "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=5"


def get_pib_rss():
    response = httpx.get(
        PIB_RSS_URL,
        timeout=30,
        follow_redirects=True
    )

    print("Status code:", response.status_code)
    print("Final URL:", response.url)
    print("Content type:", response.headers.get("content-type"))
    print("Response length:", len(response.content))
    print("\nFirst 500 characters:\n")
    print(response.text[:500])

    response.raise_for_status()

    root = ET.fromstring(response.content)

    items = []

    for item in root.findall(".//item"):
        title = item.findtext("title")
        link = item.findtext("link")
        description = item.findtext("description")
        pub_date = item.findtext("pubDate")

        items.append({
            "source": "PIB",
            "title": title,
            "link": link,
            "description": description,
            "published_date": pub_date
        })

    return items


if __name__ == "__main__":
    items = get_pib_rss()

    print(f"Found {len(items)} RSS items\n")

    for index, item in enumerate(items[:10], start=1):
        print(f"{index}. {item['title']}")
        print(f"   Date: {item['published_date']}")
        print(f"   Link: {item['link']}")
        print()