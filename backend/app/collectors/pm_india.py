import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin


PM_INDIA_URL = "https://www.pmindia.gov.in/en/news-updates/"
PM_INDIA_BASE_URL = "https://www.pmindia.gov.in"


def get_pm_news():

    response = httpx.get(
        PM_INDIA_URL,
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

    print("\n--- PAGE TITLE ---")

    print(
        soup.title.get_text(strip=True)
        if soup.title
        else "No title"
    )

    print("\n--- ALL LINKS ---\n")

    count = 0

    for link in soup.find_all("a", href=True):

        text = link.get_text(
            " ",
            strip=True
        )

        href = link.get("href")

        if text:

            print("TEXT:", text[:150])
            print("HREF:", href)
            print(
                "FULL URL:",
                urljoin(
                    PM_INDIA_BASE_URL,
                    href
                )
            )

            print("-" * 80)

            count += 1

            # Don't print hundreds of links
            if count >= 50:
                break


if __name__ == "__main__":
    get_pm_news()