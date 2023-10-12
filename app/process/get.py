# app/process/get.py
import os
import requests
from bs4 import BeautifulSoup

def get_page_info(url, session=None):

    if session is None:
        session = requests.Session()

    headers = {"Range": "bytes=0-65535"}  # Read only the first 65,535 bytes (~64kB)
    response = session.get(url, headers=headers, stream=True)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type")
    is_normal_webpage = content_type.startswith("text/html")

    if not is_normal_webpage:
        return {
            "url": response.url,
            "content_type": content_type,
        }

    html_content = response.raw.read(65535)  # Read HTML content from streaming response up to 64KB
    soup = BeautifulSoup(html_content, "lxml")

    title = soup.title.string if soup.title else None
    description = soup.find("meta", {"name": "description"})
    description = description["content"] if description else None

    favicon = soup.find("link", rel="icon")
    favicon = favicon["href"] if favicon else None

    image = soup.find("meta", {"property": "og:image"})
    image = image["content"] if image else None

    return {
        "url": response.url,
        "content_type": content_type,
        "title": title,
        "description": description,
        "favicon": favicon,
        "image": image
    }

if __name__ == "__main__":
    url = "https://www.example.com"
    with requests.Session() as session:
        page_info = get_page_info(url, session)
        print(page_info)
