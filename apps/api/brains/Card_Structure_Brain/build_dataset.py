"""Create a structure-learning dataset from Scryfall bulk data."""

import json
from pathlib import Path

from .features import build_vocab
from .config import SCRYFALL_BULK_PATH, STRUCTURE_DATASET_PATH, STRUCTURE_VOCAB_PATH
from .labels import PRIMARY_TYPES, COLOR_BUCKETS, RARITIES, MANA_VALUE_BUCKETS


def color_bucket(colors: list[str]) -> str:
    if not colors:
        return 'Colorless'
    key = ''.join(sorted(colors))
    if key in COLOR_BUCKETS:
        return key
    return 'Multicolor'


def primary_type(type_line: str) -> str:
    for candidate in PRIMARY_TYPES[:-1]:
        if candidate in type_line:
            return candidate
    return 'Other'


def mv_bucket(cmc: float) -> str:
    if cmc >= 6:
        return '6+'
    return str(int(cmc))


def normalize_card(card: dict) -> dict | None:
    if card.get('digital'):
        return None
    if card.get('layout') in {'token', 'double_faced_token', 'emblem', 'art_series'}:
        return None

    rarity = card.get('rarity', '').lower()
    if rarity not in RARITIES:
        return None

    type_line = card.get('type_line', '')
    p_type = primary_type(type_line)
    colors = card.get('colors') or []
    legendary = 'Legendary' in type_line
    needs_pt = p_type == 'Creature'
    needs_loyalty = p_type == 'Planeswalker'

    return {
        'name': card.get('name', ''),
        'primary_type': p_type,
        'color_bucket': color_bucket(colors),
        'rarity': rarity,
        'mana_value_bucket': mv_bucket(float(card.get('cmc', 0))),
        'needs_pt': int(needs_pt),
        'needs_loyalty': int(needs_loyalty),
        'is_legendary': int(legendary),
        'type_line': type_line,
        'mana_cost': card.get('mana_cost', ''),
    }


def main() -> None:
    raw_cards = json.loads(Path(SCRYFALL_BULK_PATH).read_text(encoding='utf-8'))
    rows = []
    for card in raw_cards:
        normalized = normalize_card(card)
        if normalized:
            rows.append(normalized)

    STRUCTURE_DATASET_PATH.write_text(
        '\n'.join(json.dumps(row) for row in rows),
        encoding='utf-8',
    )

    vocab = build_vocab(row['name'] for row in rows)
    STRUCTURE_VOCAB_PATH.write_text(json.dumps(vocab, indent=2), encoding='utf-8')
    print(f'Wrote {len(rows)} rows to {STRUCTURE_DATASET_PATH}')
    print(f'Vocab size: {len(vocab)}')


if __name__ == '__main__':
    main()
