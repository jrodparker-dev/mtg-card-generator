import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

from .config import ART_CACHE_DIR, ART_METADATA_JSONL, IMAGE_SIZE

TOKEN_RE = re.compile(r"[A-Za-z']+")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "")][:24]


def build_vocab(rows: list[dict], max_vocab: int = 4096) -> dict[str, int]:
    counter = Counter()
    for row in rows:
        counter.update(tokenize(row.get("prompt", "")))
    vocab = {"<PAD>": 0, "<UNK>": 1}
    for tok, _ in counter.most_common(max_vocab - 2):
        vocab[tok] = len(vocab)
    return vocab


def encode_prompt(prompt: str, vocab: dict[str, int], max_len: int = 24) -> list[int]:
    ids = [vocab.get(t, 1) for t in tokenize(prompt)[:max_len]]
    if len(ids) < max_len:
        ids.extend([0] * (max_len - len(ids)))
    return ids


class ArtDataset(Dataset):
    def __init__(self, rows: list[dict], vocab: dict[str, int]):
        self.rows = rows
        self.vocab = vocab

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx: int):
        row = self.rows[idx]
        image_path = row.get("image_path")
        if not image_path:
            image_path = str(ART_CACHE_DIR / f"{row['id']}.jpg")
        img = Image.open(image_path).convert("RGB").resize((IMAGE_SIZE, IMAGE_SIZE))
        arr = np.asarray(img, dtype=np.float32) / 127.5 - 1.0
        arr = np.transpose(arr, (2, 0, 1))
        prompt_ids = np.asarray(encode_prompt(row.get("prompt", ""), self.vocab), dtype=np.int64)
        return torch.tensor(arr), torch.tensor(prompt_ids)


def load_rows() -> list[dict]:
    rows = []
    if not ART_METADATA_JSONL.exists():
        return rows
    with ART_METADATA_JSONL.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows
