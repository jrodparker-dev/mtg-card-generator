import json
import random
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, random_split

from .config import BATCH_SIZE, EPOCHS, LABEL_MAPS_JSON, LEARNING_RATE, MODEL_STATE, RANDOM_SEED, TRAIN_ROWS_JSONL, TRAINING_META_JSON
from .dataset import MechanicsDataset, load_rows
from .label_spaces import build_label_maps, save_label_maps
from .model import MechanicsBrainModel


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def collate(batch):
    return {
        "x": torch.stack([b["x"] for b in batch]),
        "trigger": torch.stack([b["trigger"] for b in batch]),
        "complexity": torch.stack([b["complexity"] for b in batch]),
        "line_count": torch.stack([b["line_count"] for b in batch]),
        "keywords": torch.stack([b["keywords"] for b in batch]),
        "effects": torch.stack([b["effects"] for b in batch]),
        "sample_weight": torch.stack([b["sample_weight"] for b in batch]),
    }


def weighted_bce(logits, targets, weights):
    loss = nn.functional.binary_cross_entropy_with_logits(logits, targets, reduction="none").mean(dim=1)
    return (loss * weights).mean()


def weighted_ce(logits, targets, weights):
    loss = nn.functional.cross_entropy(logits, targets, reduction="none")
    return (loss * weights).mean()


def evaluate(model, loader):
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        for batch in loader:
            out = model(batch["x"])
            w = batch["sample_weight"]
            loss = (
                weighted_ce(out["trigger"], batch["trigger"], w)
                + weighted_ce(out["complexity"], batch["complexity"], w)
                + weighted_ce(out["line_count"], batch["line_count"], w)
                + weighted_bce(out["keywords"], batch["keywords"], w)
                + weighted_bce(out["effects"], batch["effects"], w)
            )
            total += float(loss.item()) * len(w)
            count += len(w)
    return total / max(1, count)


def main() -> None:
    set_seed(RANDOM_SEED)
    rows = load_rows(TRAIN_ROWS_JSONL)
    maps = build_label_maps(rows)
    save_label_maps(maps)
    dataset = MechanicsDataset(rows, maps)

    n_val = max(512, int(len(dataset) * 0.1))
    n_val = min(n_val, len(dataset) // 5 if len(dataset) > 1000 else max(1, len(dataset) // 10))
    n_train = len(dataset) - n_val
    train_ds, val_ds = random_split(dataset, [n_train, n_val], generator=torch.Generator().manual_seed(RANDOM_SEED))

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collate)

    sample = dataset[0]
    input_dim = int(sample["x"].shape[0])
    model = MechanicsBrainModel(
        input_dim=input_dim,
        num_triggers=len(maps["triggers"]),
        num_complexities=len(maps["complexities"]),
        num_line_counts=len(maps["line_counts"]),
        num_keywords=len(maps["keywords"]),
        num_effects=len(maps["effects"]),
    )
    opt = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    best_val = float("inf")
    MODEL_STATE.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, EPOCHS + 1):
        model.train()
        running = 0.0
        seen = 0
        for batch in train_loader:
            opt.zero_grad()
            out = model(batch["x"])
            w = batch["sample_weight"]
            loss = (
                weighted_ce(out["trigger"], batch["trigger"], w)
                + weighted_ce(out["complexity"], batch["complexity"], w)
                + weighted_ce(out["line_count"], batch["line_count"], w)
                + weighted_bce(out["keywords"], batch["keywords"], w)
                + weighted_bce(out["effects"], batch["effects"], w)
            )
            loss.backward()
            opt.step()
            running += float(loss.item()) * len(w)
            seen += len(w)
        train_loss = running / max(1, seen)
        val_loss = evaluate(model, val_loader)
        print(json.dumps({"epoch": epoch, "train_loss": round(train_loss, 4), "val_loss": round(val_loss, 4)}))
        if val_loss < best_val:
            best_val = val_loss
            torch.save(model.state_dict(), MODEL_STATE)

    TRAINING_META_JSON.write_text(json.dumps({"input_dim": input_dim, "best_val_loss": best_val}, indent=2), encoding="utf-8")
    print(json.dumps({"saved_model": str(MODEL_STATE), "saved_maps": str(LABEL_MAPS_JSON), "saved_meta": str(TRAINING_META_JSON)}, indent=2))


if __name__ == "__main__":
    main()
