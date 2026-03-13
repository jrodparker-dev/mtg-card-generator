import json
import re
from .config import ART_CACHE_DIR, ART_METADATA_JSONL, SCRYFALL_DEFAULT_CARDS


TOKEN_RE = re.compile(r"[A-Za-z']+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "") if len(t) >= 3]


def build_metadata_rows() -> int:
    if not SCRYFALL_DEFAULT_CARDS.exists():
        raise FileNotFoundError("Download Scryfall default cards first.")

    cards = json.loads(SCRYFALL_DEFAULT_CARDS.read_text(encoding="utf-8"))
    rows = []
    missing_images = 0
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

        image_path = ART_CACHE_DIR / f"{card['id']}.jpg"
        if not image_path.exists():
            missing_images += 1
            continue

        rows.append({
            "id": card["id"],
            "name": card.get("name", ""),
            "prompt": " ".join(tokens),
            "colors": colors,
            "types": types,
            "rarity": card.get("rarity", "common"),
            "image_url": art_crop,
            "image_path": str(image_path),
        })

    with ART_METADATA_JSONL.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")

    if missing_images:
        print(f"Skipped {missing_images} rows without a downloaded art image.")
    return len(rows)


if __name__ == "__main__":
    print(build_metadata_rows())
