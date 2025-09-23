"""Simple client to query the HouGarden Finder Ray Serve endpoint."""
import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv

API_URL_ENV = "HGFINDER_API_URL"
DEFAULT_API_URL = "http://127.0.0.1:8701/finder/generate"


def _load_env() -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(root, ".env"), override=False)
    load_dotenv(os.path.join(root, ".env.secret"), override=False)


def send_query(query: str, context: Dict[str, Any] | None = None, api_url: str | None = None) -> Dict[str, Any]:
    """Send a query to the HouGarden Finder service and return the JSON response."""
    _load_env()


    url = api_url or os.getenv(API_URL_ENV, DEFAULT_API_URL)
    payload: Dict[str, Any] = {"query": query}
    if context:
        payload["context"] = context

    session = requests.Session()
    session.trust_env = False  # ignore system proxy settings (e.g., v2ray)
    resp = session.post(url, json=payload, timeout=30, proxies={})
    try:
        resp.raise_for_status()
    except requests.HTTPError as err:
        detail = ""
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"Request failed with status {resp.status_code}: {detail}") from err
    return resp.json()


def main() -> None:
    os.environ['NO_PROXY'] = "localhost;127.0.0.1"
    query = os.getenv("HGFINDER_QUERY", "Flat Bush 有哪些房子？， page=2,pageSize=5")
    context = {}
    response = send_query(query=query, context=context)
    print("Request URL:", os.getenv(API_URL_ENV, DEFAULT_API_URL))
    print("Query:", query)
    print("Response:")
    print(response)


if __name__ == "__main__":
    main()
