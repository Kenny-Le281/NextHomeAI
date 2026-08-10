from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests


MINIMUM_PROPERTY_PAGE_BYTES = 10_000


def _is_usable_property_page(response):
    content = response.content
    lowered = content[:10_000].lower()
    return (
        response.ok
        and len(content) >= MINIMUM_PROPERTY_PAGE_BYTES
        and b"are you a robot" not in lowered
    )


def _add_crawler_query(url):
    parsed = urlsplit(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.setdefault("utm_source", "google")
    query.setdefault("utm_medium", "organic")
    return urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment)
    )

def fetch_html(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-CA,en;q=0.9",
    }
    response = requests.get(url, headers=headers, timeout=30)
    if _is_usable_property_page(response):
        return response.text

    # Redfin occasionally serves an empty or robot-check response to ordinary
    # HTTP clients while still exposing its public structured metadata to link
    # preview crawlers.
    crawler_headers = {
        "User-Agent": "facebookexternalhit/1.1",
        "Accept-Language": "en-CA,en;q=0.9",
    }
    fallback = requests.get(
        _add_crawler_query(url),
        headers=crawler_headers,
        timeout=30,
    )
    if _is_usable_property_page(fallback):
        return fallback.text

    status = fallback.status_code if fallback.status_code else response.status_code
    raise RuntimeError(f"Redfin returned a blocked or empty property page ({status}).")
