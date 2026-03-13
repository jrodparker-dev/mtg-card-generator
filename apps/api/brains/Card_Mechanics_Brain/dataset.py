import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import Dataset

from .label_spaces import load_label_maps
from .vectorizers import shell_to_vector


@dataclass
class EncodedTargets:
    trigger: int
    complexity: int
    line_count: int
    keywords: np.ndarray
    effects: np.ndarray


class MechanicsDataset(Dataset):
    def __init__(self, rows: list[dict[str, Any]], maps: dict[str, Any]):
        self.rows = rows
        self.maps = maps
        self.subtype_vocab = maps["subtypes"]
        self.keyword_vocab = maps["keywords"]
        self.effect_vocab = maps["effects"]
        self.trigger_vocab = maps["triggers"]
        self.complexity_vocab = maps["complexities"]
        self.line_vocab = maps["line_counts"]

    def __len__(self) -> int:
        return len(self.rows)

    def _encode_targets(self, row: dict[str, Any]) -> EncodedTargets:
        kw = np.asarray([1.0 if k in set(row.get("keywords") or []) else 0.0 for k in self.keyword_vocab], dtype=np.float32)
        fx = np.asarray([1.0 if e in set(row.get("effects") or []) else 0.0 for e in self.effect_vocab], dtype=np.float32)
        return EncodedTargets(
            trigger=self.trigger_vocab.index(row["trigger"]),
            complexity=self.complexity_vocab.index(row["complexity"]),
            line_count=self.line_vocab.index(max(1, min(5, int(row["line_count"])))),
            keywords=kw,
            effects=fx,
        )

    def __getitem__(self, idx: int) -> dict[str, Any]:
        row = self.rows[idx]
        x = shell_to_vector(row, self.subtype_vocab)
        y = self._encode_targets(row)
        return {
            "x": torch.tensor(x, dtype=torch.float32),
            "trigger": torch.tensor(y.trigger, dtype=torch.long),
            "complexity": torch.tensor(y.complexity, dtype=torch.long),
            "line_count": torch.tensor(y.line_count, dtype=torch.long),
            "keywords": torch.tensor(y.keywords, dtype=torch.float32),
            "effects": torch.tensor(y.effects, dtype=torch.float32),
            "sample_weight": torch.tensor(float(row.get("sample_weight", 1.0)), dtype=torch.float32),
            "row": row,
        }


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows
