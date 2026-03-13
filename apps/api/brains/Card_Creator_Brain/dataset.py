import json
import re
from collections import Counter

import torch
from torch.utils.data import Dataset

from .config import DATASET_JSONL, MAX_NAME_TOKENS

TOKEN_RE = re.compile(r"[A-Za-z']+")

def load_rows():
    rows = []
    with DATASET_JSONL.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def tokenize(text: str):
    return [t.lower() for t in TOKEN_RE.findall(text or "")][:MAX_NAME_TOKENS]

def build_vocab(rows, max_vocab=4096):
    counter = Counter()
    for row in rows:
        counter.update(row.get("name_tokens") or tokenize(row.get("name", "")))
    vocab = {"<PAD>": 0, "<UNK>": 1}
    for tok, _ in counter.most_common(max_vocab - 2):
        vocab[tok] = len(vocab)
    return vocab

def encode_tokens(tokens, vocab):
    ids = [vocab.get(t, 1) for t in tokens[:MAX_NAME_TOKENS]]
    if len(ids) < MAX_NAME_TOKENS:
        ids.extend([0] * (MAX_NAME_TOKENS - len(ids)))
    return ids

def build_label_maps(rows):
    def unique(key):
        vals = set()
        for row in rows:
            value = row[key]
            if isinstance(value, list):
                vals.update(value)
            else:
                vals.add(value)
        return sorted(vals)

    return {
        "primary_type": unique("primary_type"),
        "rarity": unique("rarity"),
        "color_bucket": unique("color_bucket"),
        "mana_value_bucket": unique("mana_value_bucket"),
        "trigger": unique("trigger"),
        "effects": unique("effects"),
        "keywords": unique("keywords"),
    }

class CreatorBrainDataset(Dataset):
    def __init__(self, rows, vocab, label_maps):
        self.rows = rows
        self.vocab = vocab
        self.label_maps = label_maps

    def __len__(self):
        return len(self.rows)

    def _multi_hot(self, values, vocab):
        out = torch.zeros(len(vocab), dtype=torch.float32)
        idx = {v: i for i, v in enumerate(vocab)}
        for value in values:
            if value in idx:
                out[idx[value]] = 1.0
        return out

    def __getitem__(self, idx):
        row = self.rows[idx]
        tokens = row.get("name_tokens") or tokenize(row.get("name", ""))
        x = torch.tensor(encode_tokens(tokens, self.vocab), dtype=torch.long)

        single = {}
        for key in ["primary_type", "rarity", "color_bucket", "mana_value_bucket", "trigger"]:
            single[key] = torch.tensor(self.label_maps[key].index(row[key]), dtype=torch.long)

        flags = torch.tensor([
            1.0 if row.get("needs_pt") else 0.0,
            1.0 if row.get("needs_loyalty") else 0.0,
            1.0 if row.get("is_legendary") else 0.0,
        ], dtype=torch.float32)

        multi = {
            "effects": self._multi_hot(row.get("effects", []), self.label_maps["effects"]),
            "keywords": self._multi_hot(row.get("keywords", []), self.label_maps["keywords"]),
        }

        return {"tokens": x, "single": single, "flags": flags, "multi": multi}
