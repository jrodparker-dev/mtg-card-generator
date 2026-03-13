import re
from collections import Counter
from typing import Any

KEYWORD_CANDIDATES = [
    "Flying", "Haste", "Vigilance", "Trample", "First strike", "Double strike",
    "Deathtouch", "Lifelink", "Menace", "Reach", "Ward", "Hexproof",
    "Indestructible", "Prowess", "Defender", "Flash", "Vigilance",
    "Skulk", "Fear", "Shadow", "Horsemanship", "Toxic", "Infect",
]

EFFECT_PATTERNS: dict[str, list[str]] = {
    "draw": [r"draw (?:a|two|three|\d+) card"],
    "damage": [r"deals? \d+ damage", r"deals? damage equal to"],
    "token": [r"create(?:s)? (?:a|an|two|three|X|\d+) .* token"],
    "treasure": [r"create(?:s)? .* Treasure token"],
    "food": [r"create(?:s)? .* Food token"],
    "clue": [r"create(?:s)? .* Clue token"],
    "map": [r"create(?:s)? .* Map token"],
    "ramp": [r"add \{", r"search your library .* land"],
    "removal": [r"destroy target", r"exile target", r"target creature gets -\d+/[-+]?\d+"],
    "bounce": [r"return target .* to (?:its|their) owner's hand"],
    "discard": [r"discard(?:s)? (?:a|two|three|\d+) card"],
    "mill": [r"mill (?:a|two|three|\d+) card"],
    "scry": [r"scry \d+"],
    "surveil": [r"surveil \d+"],
    "loot": [r"draw a card.*discard a card", r"discard a card.*draw a card"],
    "lifegain": [r"you gain \d+ life", r"gain life equal to"],
    "reanimate": [r"return target .* from your graveyard to the battlefield"],
    "recur_hand": [r"return target .* from your graveyard to your hand"],
    "sacrifice": [r"sacrifice (?:a|an|another|two|three|\d+|X)"],
    "tap": [r"tap target"],
    "untap": [r"untap target", r"untap up to"],
    "counters": [r"put (?:a|an|two|three|\d+|X) .* counter"],
    "counterspell": [r"counter target spell"],
    "impulse": [r"exile the top .* you may play"],
    "blink": [r"exile up to .* return"],
}

TRIGGER_RULES: list[tuple[str, str]] = [
    ("etb", r"when(?:ever)? .* enters the battlefield"),
    ("dies", r"when(?:ever)? .* dies"),
    ("attack", r"whenever .* attacks"),
    ("combat_damage_to_player", r"whenever .* deals combat damage to a player"),
    ("upkeep", r"at the beginning of (?:your|each) upkeep"),
    ("end_step", r"at the beginning of the end step"),
    ("cast", r"whenever you cast"),
    ("activated", r"^[^\n]*:\s"),
    ("static", r"as long as|if .* would|spells you cast|creatures you control"),
]

COMPLEXITY_RULES = [
    ("complex", 4),
    ("medium", 2),
    ("simple", 0),
]


def normalize_oracle(text: str) -> str:
    text = text or ""
    text = text.replace("\u2014", "—")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_lines(text: str) -> list[str]:
    if not text:
        return []
    text = text.replace("\r\n", "\n")
    return [line.strip() for line in text.split("\n") if line.strip()]


def extract_keywords(card: dict[str, Any]) -> list[str]:
    keywords = list(card.get("keywords") or [])
    oracle = card.get("oracle_text") or ""
    for kw in KEYWORD_CANDIDATES:
        if re.search(rf"\b{re.escape(kw)}\b", oracle, flags=re.I):
            keywords.append(kw)
    seen = set()
    out = []
    for kw in keywords:
        k = kw.strip()
        if k and k.lower() not in seen:
            seen.add(k.lower())
            out.append(k)
    return out


def detect_trigger(oracle_text: str) -> str:
    text = normalize_oracle(oracle_text)
    for label, pattern in TRIGGER_RULES:
        if re.search(pattern, text, flags=re.I):
            return label
    return "none"


def detect_effects(oracle_text: str) -> list[str]:
    text = normalize_oracle(oracle_text)
    out = []
    for effect, patterns in EFFECT_PATTERNS.items():
        if any(re.search(p, text, flags=re.I) for p in patterns):
            out.append(effect)
    return out or ["vanilla"]


def compute_complexity(lines: list[str], keywords: list[str], effects: list[str]) -> str:
    score = len(lines) + len(keywords) + len([e for e in effects if e != "vanilla"])
    for label, threshold in COMPLEXITY_RULES:
        if score >= threshold:
            return label
    return "simple"


def count_text_lines(card: dict[str, Any]) -> int:
    return max(1, min(5, len(split_lines(card.get("oracle_text") or "")) or len(extract_keywords(card))))


def parse_card_mechanics(card: dict[str, Any]) -> dict[str, Any]:
    oracle = card.get("oracle_text") or ""
    lines = split_lines(oracle)
    keywords = extract_keywords(card)
    effects = detect_effects(oracle)
    trigger = detect_trigger(oracle)
    complexity = compute_complexity(lines, keywords, effects)
    return {
        "keywords": keywords,
        "effects": effects,
        "trigger": trigger,
        "complexity": complexity,
        "line_count": count_text_lines(card),
    }


def top_counts(rows: list[dict[str, Any]], field: str) -> Counter:
    c = Counter()
    for row in rows:
        value = row.get(field)
        if isinstance(value, list):
            c.update(value)
        elif value is not None:
            c[value] += 1
    return c
