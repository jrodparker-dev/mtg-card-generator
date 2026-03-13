from typing import Any

import numpy as np

COLORS = ["W", "U", "B", "R", "G", "C"]
CARD_TYPES = ["Creature", "Planeswalker", "Instant", "Sorcery", "Artifact", "Enchantment", "Land", "Battle", "Unknown"]
RARITIES = ["Common", "Uncommon", "Rare", "Mythic"]

NAME_TOKENS = {
    "angel": [1,0,0,0,0,1,0,0],
    "dragon": [0,0,0,1,0,1,0,0],
    "goblin": [0,0,0,1,0,1,0,0],
    "elf": [0,0,0,0,1,1,0,0],
    "zombie": [0,0,1,0,0,1,0,0],
    "wizard": [0,1,0,0,0,1,0,0],
    "cathedral": [1,0,0,0,0,0,0,1],
    "void": [0,1,1,0,0,0,1,0],
    "flame": [0,0,0,1,0,0,0,0],
    "growth": [0,0,0,0,1,0,0,0],
    "tax": [1,0,0,0,0,0,0,1],
    "engine": [0,0,0,0,0,0,1,0],
}


def _multi_hot(items: list[str], vocab: list[str]) -> list[float]:
    item_set = set(items)
    return [1.0 if v in item_set else 0.0 for v in vocab]


def _one_hot(item: str, vocab: list[str]) -> list[float]:
    return [1.0 if item == v else 0.0 for v in vocab]


def _name_features(name: str) -> list[float]:
    tokens = (name or "").lower().replace("-", " ").split()
    if not tokens:
        return [0.0] * 8
    out = np.zeros(8, dtype=np.float32)
    for token in tokens:
        if token in NAME_TOKENS:
            out += np.array(NAME_TOKENS[token], dtype=np.float32)
    out = np.clip(out, 0.0, 2.0)
    return out.tolist()


def shell_to_vector(shell: dict[str, Any], subtype_vocab: list[str]) -> np.ndarray:
    colors = list(shell.get("colors") or []) or ["C"]
    primary_type = next(iter(shell.get("types") or [shell.get("primary_type") or "Unknown"]), "Unknown")
    rarity = shell.get("rarity") or "Common"
    subtypes = list(shell.get("subtypes") or [])
    mana_value = float(shell.get("manaValue", shell.get("mana_value", 0)) or 0)

    parts = []
    parts.extend(_multi_hot(colors, COLORS))
    parts.extend(_one_hot(primary_type, CARD_TYPES))
    parts.extend(_one_hot(rarity, RARITIES))
    parts.extend(_multi_hot(subtypes, subtype_vocab))
    parts.extend([
        min(mana_value, 10.0) / 10.0,
        1.0 if shell.get("isLegendary") or shell.get("is_legendary") else 0.0,
        1.0 if shell.get("needsPowerToughness") or shell.get("needs_pt") else 0.0,
        1.0 if shell.get("needsLoyalty") or shell.get("needs_loyalty") else 0.0,
    ])
    parts.extend(_name_features(shell.get("name") or ""))
    return np.asarray(parts, dtype=np.float32)
