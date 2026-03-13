import json
from pathlib import Path
from typing import Any

from .config import MIN_LABEL_FREQ, PROCESSED_DIR, SCRYFALL_DEFAULT_CARDS, TRAIN_ROWS_JSONL
from .oracle_parser import parse_card_mechanics

LEGAL_TYPES = {"Creature", "Artifact", "Enchantment", "Instant", "Sorcery", "Land", "Planeswalker", "Battle"}
RARITIES = {"common", "uncommon", "rare", "mythic"}


def is_usable(card: dict[str, Any]) -> bool:
    if card.get("lang") != "en":
        return False
    if card.get("digital"):
        return False
    if card.get("set_type") in {"minigame", "memorabilia", "token", "art_series"}:
        return False
    if card.get("layout") in {"token", "art_series", "scheme", "planar", "double_faced_token", "emblem", "augment", "host"}:
        return False
    if card.get("rarity") not in RARITIES:
        return False
    type_line = card.get("type_line") or ""
    return any(t in type_line for t in LEGAL_TYPES)


def primary_type(card: dict[str, Any]) -> str:
    type_line = card.get("type_line") or ""
    for t in ["Creature", "Planeswalker", "Instant", "Sorcery", "Artifact", "Enchantment", "Land", "Battle"]:
        if t in type_line:
            return t
    return "Unknown"


def release_year(card: dict[str, Any]) -> int:
    released = str(card.get("released_at") or "")
    if len(released) >= 4 and released[:4].isdigit():
        return int(released[:4])
    return 2000


def recent_weight(year: int) -> float:
    if year >= 2022:
        return 1.0
    if year >= 2018:
        return 0.75
    if year >= 2010:
        return 0.45
    return 0.2


def build_row(card: dict[str, Any]) -> dict[str, Any]:
    parsed = parse_card_mechanics(card)
    power = card.get("power")
    toughness = card.get("toughness")
    loyalty = card.get("loyalty")
    return {
        "name": card.get("name"),
        "mana_cost": card.get("mana_cost") or "",
        "mana_value": int(card.get("cmc") or 0),
        "colors": card.get("colors") or [],
        "color_identity": card.get("color_identity") or [],
        "type_line": card.get("type_line") or "",
        "primary_type": primary_type(card),
        "subtypes": [x.strip() for x in (card.get("type_line") or "").split("—")[-1].split()] if "—" in (card.get("type_line") or "") else [],
        "rarity": str(card.get("rarity") or "common").capitalize(),
        "is_legendary": "Legendary" in (card.get("type_line") or ""),
        "needs_pt": power is not None and toughness is not None,
        "needs_loyalty": loyalty is not None,
        "power": str(power) if power is not None else None,
        "toughness": str(toughness) if toughness is not None else None,
        "loyalty": str(loyalty) if loyalty is not None else None,
        "released_year": release_year(card),
        "sample_weight": recent_weight(release_year(card)),
        **parsed,
        "oracle_text": (card.get("oracle_text") or "").strip(),
    }


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    cards = json.loads(SCRYFALL_DEFAULT_CARDS.read_text(encoding="utf-8"))
    rows = [build_row(card) for card in cards if is_usable(card)]
    with TRAIN_ROWS_JSONL.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"rows": len(rows), "saved": str(TRAIN_ROWS_JSONL)}, indent=2))


if __name__ == "__main__":
    main()
