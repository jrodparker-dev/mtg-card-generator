import json
import re

from .config import DATASET_JSONL, SCRYFALL_DEFAULT_CARDS

TOKEN_RE = re.compile(r"[A-Za-z']+")

TYPE_VOCAB = ["Creature", "Instant", "Sorcery", "Artifact", "Enchantment", "Land", "Planeswalker", "Battle"]
RARITY_MAP = {"common": "Common", "uncommon": "Uncommon", "rare": "Rare", "mythic": "Mythic"}
COLOR_BUCKETS = {
    "": "Colorless",
    "W": "W", "U": "U", "B": "B", "R": "R", "G": "G",
    "WU": "W/U", "WB": "W/B", "WR": "W/R", "WG": "W/G",
    "UB": "U/B", "UR": "U/R", "UG": "U/G",
    "BR": "B/R", "BG": "B/G", "RG": "R/G",
}

def to_bucket(colors):
    joined = "".join(colors or [])
    return COLOR_BUCKETS.get(joined, joined or "Colorless")

def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "")][:16]

def infer_effects(oracle: str) -> list[str]:
    t = (oracle or "").lower()
    effects = []
    if "draw" in t:
        effects.append("draw")
    if "damage" in t or "deals" in t:
        effects.append("damage")
    if "treasure" in t:
        effects.append("treasure")
    if "token" in t or "create " in t:
        effects.append("token")
    if "gain " in t and "life" in t:
        effects.append("lifegain")
    if "destroy target" in t or "exile target" in t:
        effects.append("removal")
    if "discard" in t:
        effects.append("discard")
    if "mill" in t:
        effects.append("mill")
    if "+1/+1 counter" in t or "counter on" in t:
        effects.append("counters")
    if "add {" in t:
        effects.append("ramp")
    if "look at the top" in t or "impulse" in t:
        effects.append("impulse")
    return effects[:3] or ["vanilla"]

def infer_keywords(oracle: str) -> list[str]:
    t = (oracle or "").lower()
    keywords = []
    for key in ["flying", "trample", "vigilance", "haste", "deathtouch", "lifelink", "menace", "ward", "flash", "first strike", "double strike", "reach"]:
        if key in t:
            keywords.append(key)
    return keywords[:3]

def infer_trigger(oracle: str) -> str:
    t = (oracle or "").lower()
    if "when " in t and " enters the battlefield" in t:
        return "etb"
    if "whenever " in t and " attacks" in t:
        return "attack"
    if "dies" in t or ("when " in t and " dies" in t):
        return "dies"
    if "combat damage to a player" in t:
        return "combat_damage_to_player"
    if "at the beginning of your upkeep" in t:
        return "upkeep"
    if ":" in t:
        return "activated"
    if any(k in t for k in ["flying", "deathtouch", "lifelink", "vigilance", "menace"]):
        return "static"
    return "none"

def build_dataset():
    cards = json.loads(SCRYFALL_DEFAULT_CARDS.read_text(encoding="utf-8"))
    rows = []
    for card in cards:
        if card.get("layout") not in (None, "normal"):
            continue
        if card.get("set_type") in {"token", "memorabilia", "minigame"}:
            continue
        name = card.get("name", "")
        colors = card.get("colors") or []
        type_line = card.get("type_line", "")
        primary_type = type_line.split(" — ")[0].split()[0] if type_line else "Creature"
        if primary_type not in TYPE_VOCAB:
            continue
        oracle = card.get("oracle_text", "") or ""
        rarity = RARITY_MAP.get(card.get("rarity", "common"), "Common")
        mana_value = int(card.get("cmc", 0) or 0)
        mana_bucket = "6+" if mana_value >= 6 else str(mana_value)
        subtype_part = type_line.split(" — ", 1)[1] if " — " in type_line else ""
        subtypes = subtype_part.split()[:4]
        rows.append({
            "name": name,
            "name_tokens": tokenize(name),
            "primary_type": primary_type,
            "type_line": type_line,
            "rarity": rarity,
            "color_bucket": to_bucket(colors),
            "mana_value_bucket": mana_bucket,
            "needs_pt": "Creature" in type_line,
            "needs_loyalty": "Planeswalker" in type_line,
            "is_legendary": "Legendary" in type_line,
            "subtypes": subtypes,
            "trigger": infer_trigger(oracle),
            "effects": infer_effects(oracle),
            "keywords": infer_keywords(oracle),
            "oracle_text": oracle,
        })

    with DATASET_JSONL.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    print(f"wrote {len(rows)} rows to {DATASET_JSONL}")

if __name__ == "__main__":
    build_dataset()
