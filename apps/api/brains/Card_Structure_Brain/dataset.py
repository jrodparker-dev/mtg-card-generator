import json
from pathlib import Path

import torch
from torch.utils.data import Dataset

from .features import encode_name
from .labels import PRIMARY_TYPES, COLOR_BUCKETS, RARITIES, MANA_VALUE_BUCKETS


class CardStructureDataset(Dataset):
    def __init__(self, dataset_path: Path, vocab_path: Path):
        self.rows = [json.loads(line) for line in dataset_path.read_text(encoding='utf-8').splitlines() if line.strip()]
        self.vocab = json.loads(vocab_path.read_text(encoding='utf-8'))

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int) -> dict:
        row = self.rows[idx]
        return {
            'tokens': torch.tensor(encode_name(row['name'], self.vocab), dtype=torch.long),
            'primary_type': torch.tensor(PRIMARY_TYPES.index(row['primary_type']), dtype=torch.long),
            'color_bucket': torch.tensor(COLOR_BUCKETS.index(row['color_bucket']), dtype=torch.long),
            'rarity': torch.tensor(RARITIES.index(row['rarity']), dtype=torch.long),
            'mana_value_bucket': torch.tensor(MANA_VALUE_BUCKETS.index(row['mana_value_bucket']), dtype=torch.long),
            'needs_pt': torch.tensor(row['needs_pt'], dtype=torch.float32),
            'needs_loyalty': torch.tensor(row['needs_loyalty'], dtype=torch.float32),
            'is_legendary': torch.tensor(row['is_legendary'], dtype=torch.float32),
        }
