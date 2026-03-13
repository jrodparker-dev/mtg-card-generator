import json
from pathlib import Path
from typing import Iterable

import requests
from tqdm import tqdm

from .config import ART_CACHE_DIR, ART_METADATA_JSONL, SCRYFALL_DEFAULT_CARDS

BULK_URL = "https://api.scryfall.com/bulk-data"


def _download_default_cards_json() -> None:
    if SCRYFALL_DEFAULT_CARDS.exists():
        return
    bulk = requests.get(BULK_URL, timeout=60).json()["data"]
    row = next(item for item in bulk if item["type"] == "default_cards")
    data = requests.get(row["download_uri"], timeout=300)
    data.raise_for_status()
    SCRYFALL_DEFAULT_CARDS.write_bytes(data.content)


def iter_art_rows(limit: int | None = None) -> Iterable[dict]:
    _download_default_cards_json()
    cards = json.loads(SCRYFALL_DEFAULT_CARDS.read_text(encoding="utf-8"))
    count = 0
    for card in cards:
        if "art_crop" not in card.get("image_uris", {}):
            continue
        yield {
            "id": card["id"],
            "name": card["name"],
            "colors": card.get("colors") or [],
            "type_line": card.get("type_line") or "",
            "oracle_text": card.get("oracle_text") or "",
            "set_name": card.get("set_name") or "",
            "released_at": card.get("released_at") or "",
            "rarity": card.get("rarity") or "common",
            "art_crop": card["image_uris"]["art_crop"],
        }
        count += 1
        if limit and count >= limit:
            break


def download_art(limit: int | None = 5000) -> None:
    rows = list(iter_art_rows(limit=limit))
    with ART_METADATA_JSONL.open("w", encoding="utf-8") as fh:
        for row in tqdm(rows, desc="art refs"):
            out = ART_CACHE_DIR / f"{row['id']}.jpg"
            if not out.exists():
                try:
                    resp = requests.get(row["art_crop"], timeout=60)
                    resp.raise_for_status()
                    out.write_bytes(resp.content)
                except Exception:
                    continue
            row["image_path"] = str(out)
            fh.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    download_art()
