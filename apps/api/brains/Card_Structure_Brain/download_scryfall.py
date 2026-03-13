"""Download Scryfall default cards bulk data.

Usage:
    python brains/Card_Structure_Brain/download_scryfall.py
"""

import json
from pathlib import Path

import requests

from .config import SCRYFALL_BULK_PATH

BULK_URL = 'https://api.scryfall.com/bulk-data'


def main() -> None:
    response = requests.get(BULK_URL, timeout=60)
    response.raise_for_status()
    data = response.json()['data']
    default_cards = next(item for item in data if item['type'] == 'default_cards')
    download_url = default_cards['download_uri']

    print(f'Downloading from: {download_url}')
    bulk_response = requests.get(download_url, timeout=120)
    bulk_response.raise_for_status()

    SCRYFALL_BULK_PATH.write_bytes(bulk_response.content)
    print(f'Saved to {SCRYFALL_BULK_PATH}')


if __name__ == '__main__':
    main()
