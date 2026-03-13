import json
import re
from collections import Counter

from .config import ART_METADATA_JSONL, SCRYFALL_DEFAULT_CARDS


TOKEN_RE = re.compile(r"[A-Za-z']+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "") if len(t) >= 3]


def build_metadata_rows() -> int:
    if not SCRYFALL_DEFAULT_CARDS.exists():
        raise FileNotFoundError("Download Scryfall default cards first.")

    cards = json.loads(SCRYFALL_DEFAULT_CARDS.read_text(encoding="utf-8"))
    rows = []
    for card in cards:
        image_uris = card.get("image_uris") or {}
        art_crop = image_uris.get("art_crop")
        if not art_crop:
            continue
        colors = card.get("colors") or []
        types = (card.get("type_line") or "").split(" — ")[0].split()
        tokens = _tokenize(card.get("name", ""))[:4]
        tokens.extend(_tokenize(card.get("type_line", ""))[:4])
        tokens.extend(_tokenize(card.get("oracle_text", ""))[:8])

        rows.append({
            "id": card["id"],
            "name": card.get("name", ""),
            "prompt": " ".join(tokens),
            "colors": colors,
            "types": types,
            "rarity": card.get("rarity", "common"),
            "image_url": art_crop,
        })

    with ART_METADATA_JSONL.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    return len(rows)


if __name__ == "__main__":
    print(build_metadata_rows())
