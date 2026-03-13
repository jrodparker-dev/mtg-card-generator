import json
from collections import Counter
from pathlib import Path
from typing import Any

from .config import LABEL_MAPS_JSON, MIN_LABEL_FREQ


def build_vocab(rows: list[dict[str, Any]], field: str, min_freq: int = MIN_LABEL_FREQ) -> list[str]:
    c = Counter()
    for row in rows:
        values = row.get(field) or []
        if isinstance(values, list):
            c.update(values)
        else:
            c[values] += 1
    return [k for k, v in c.most_common() if v >= min_freq and k not in {None, "", "vanilla"}]


def build_label_maps(rows: list[dict[str, Any]]) -> dict[str, Any]:
    maps = {
        "primary_types": sorted({row["primary_type"] for row in rows}),
        "rarities": sorted({row["rarity"] for row in rows}),
        "triggers": sorted({row["trigger"] for row in rows}),
        "complexities": sorted({row["complexity"] for row in rows}),
        "keywords": build_vocab(rows, "keywords"),
        "effects": build_vocab(rows, "effects"),
        "subtypes": build_vocab(rows, "subtypes", min_freq=30),
        "colors": ["W", "U", "B", "R", "G", "C"],
        "line_counts": [1, 2, 3, 4, 5],
    }
    return maps


def save_label_maps(maps: dict[str, Any]) -> None:
    LABEL_MAPS_JSON.parent.mkdir(parents=True, exist_ok=True)
    LABEL_MAPS_JSON.write_text(json.dumps(maps, indent=2), encoding="utf-8")


def load_label_maps() -> dict[str, Any]:
    return json.loads(LABEL_MAPS_JSON.read_text(encoding="utf-8"))
