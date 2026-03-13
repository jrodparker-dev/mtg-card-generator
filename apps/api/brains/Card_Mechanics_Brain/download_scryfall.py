import json
from pathlib import Path

import requests

from .config import RAW_DIR, SCRYFALL_DEFAULT_CARDS

BULK_URL = "https://api.scryfall.com/bulk-data"


def download_default_cards() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(BULK_URL, timeout=60)
    r.raise_for_status()
    data = r.json()["data"]
    default = next(item for item in data if item["type"] == "default_cards")
    download_uri = default["download_uri"]
    file_resp = requests.get(download_uri, timeout=120)
    file_resp.raise_for_status()
    SCRYFALL_DEFAULT_CARDS.write_bytes(file_resp.content)
    return SCRYFALL_DEFAULT_CARDS


if __name__ == "__main__":
    path = download_default_cards()
    print(json.dumps({"saved": str(path)}, indent=2))
