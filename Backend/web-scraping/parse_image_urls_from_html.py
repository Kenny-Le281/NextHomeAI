import json
import re
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup


IMAGE_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
}
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def parse_image_urls_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})

    urls = []
    seen = set()

    def add_url(url):
        if not isinstance(url, str):
            return

        url = url.strip()
        parsed = urlsplit(url)
        path = parsed.path.lower()
        host = parsed.hostname or ""

        if (
            parsed.scheme in {"http", "https"}
            and path.endswith(IMAGE_EXTENSIONS)
            and (not host.endswith("cdn-redfin.com") or path.startswith("/photo/"))
            and url not in seen
        ):
            seen.add(url)
            urls.append(url)

    def collect_from_image_field(image_data):
        if isinstance(image_data, str):
            add_url(image_data)

        elif isinstance(image_data, dict):
            add_url(image_data.get("url"))

        elif isinstance(image_data, list):
            for item in image_data:
                if isinstance(item, str):
                    add_url(item)
                elif isinstance(item, dict):
                    add_url(item.get("url"))

    for script in scripts:
        script_content = script.string or script.get_text(strip=True)
        if not script_content:
            continue

        try:
            data = json.loads(script_content)
        except json.JSONDecodeError:
            continue

        data_objects = walk(data)
        for data_obj in data_objects:
            if "image" in data_obj:
                collect_from_image_field(data_obj["image"])

    # The property JSON-LD is the authoritative gallery. Returning here avoids
    # collecting photos from nearby-listing widgets elsewhere on the page.
    if urls:
        return urls

    # Redfin sometimes leaves the JSON-LD image list empty while still exposing
    # the primary property photo through social metadata or an image element.
    for meta in soup.select('meta[property="og:image"], meta[name="twitter:image"]'):
        add_url(meta.get("content"))

    for image in soup.find_all("img"):
        add_url(image.get("src"))
        add_url(image.get("data-src"))

    if urls:
        return urls

    # Some pages keep the primary photo inside application state rather than an
    # image element or JSON-LD image field.
    for embedded_url in re.findall(
        r'https?://[^"\'\\\s<>]+?\.(?:jpe?g|png|webp)(?:\?[^"\'\\\s<>]*)?',
        unescape(html_content),
        flags=re.IGNORECASE,
    ):
        add_url(embedded_url)
        if urls:
            break

    return urls


def _version_candidates(url):
    """Return nearby Redfin CDN versions for a potentially stale photo URL."""
    candidates = [url]
    parsed = urlsplit(url)

    if not (parsed.hostname or "").endswith("cdn-redfin.com"):
        return candidates

    path_match = re.match(
        r"^(?P<prefix>.*_)(?P<version>\d+)(?P<extension>\.(?:jpe?g|png|webp))$",
        parsed.path,
        flags=re.IGNORECASE,
    )
    if not path_match:
        return candidates

    version = int(path_match.group("version"))
    for distance in range(1, 7):
        for candidate_version in (version + distance, version - distance):
            if candidate_version < 1:
                continue
            candidate_path = (
                f'{path_match.group("prefix")}{candidate_version}'
                f'{path_match.group("extension")}'
            )
            candidates.append(
                urlunsplit(
                    (
                        parsed.scheme,
                        parsed.netloc,
                        candidate_path,
                        parsed.query,
                        parsed.fragment,
                    )
                )
            )

    return candidates


def _resolve_image_url(url):
    for candidate in _version_candidates(url):
        try:
            response = requests.head(
                candidate,
                headers=IMAGE_REQUEST_HEADERS,
                allow_redirects=True,
                timeout=10,
            )
        except requests.RequestException:
            continue

        content_type = response.headers.get("Content-Type", "").lower()
        is_image = response.ok and content_type.startswith("image/")
        response.close()
        if is_image:
            return candidate

    return None


def resolve_image_urls(urls, max_workers=8):
    """Remove broken URLs and refresh stale Redfin CDN version suffixes."""
    if not urls:
        return []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        resolved = list(executor.map(_resolve_image_url, urls))

    unique_urls = []
    seen = set()
    for url in resolved:
        if url and url not in seen:
            seen.add(url)
            unique_urls.append(url)

    return unique_urls


def walk(node):
    collected_nodes = []
    if isinstance(node, dict):
        collected_nodes.append(node)
        for value in node.values():
            collected_nodes.extend(walk(value))

    elif isinstance(node, list):
        for item in node:
            collected_nodes.extend(walk(item))

    return collected_nodes
