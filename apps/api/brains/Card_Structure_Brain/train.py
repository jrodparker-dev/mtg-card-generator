import json

import torch
from torch import nn
from torch.utils.data import DataLoader, random_split

from .config import STRUCTURE_DATASET_PATH, STRUCTURE_MODEL_PATH, STRUCTURE_VOCAB_PATH
from .dataset import CardStructureDataset
from .model import CardStructureBrain

BATCH_SIZE = 128
EPOCHS = 5
LR = 1e-3


def collate_fn(batch: list[dict]) -> dict:
    keys = batch[0].keys()
    return {key: torch.stack([item[key] for item in batch]) for key in keys}


def compute_loss(outputs: dict, batch: dict) -> torch.Tensor:
    ce = nn.CrossEntropyLoss()
    bce = nn.BCEWithLogitsLoss()
    return (
        ce(outputs['primary_type'], batch['primary_type'])
        + ce(outputs['color_bucket'], batch['color_bucket'])
        + ce(outputs['rarity'], batch['rarity'])
        + ce(outputs['mana_value_bucket'], batch['mana_value_bucket'])
        + bce(outputs['needs_pt'], batch['needs_pt'])
        + bce(outputs['needs_loyalty'], batch['needs_loyalty'])
        + bce(outputs['is_legendary'], batch['is_legendary'])
    )


def main() -> None:
    dataset = CardStructureDataset(STRUCTURE_DATASET_PATH, STRUCTURE_VOCAB_PATH)
    train_size = int(0.9 * len(dataset))
    val_size = len(dataset) - train_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collate_fn)

    vocab = json.loads(STRUCTURE_VOCAB_PATH.read_text(encoding='utf-8'))
    model = CardStructureBrain(vocab_size=len(vocab))
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0.0
        for batch in train_loader:
            optimizer.zero_grad()
            outputs = model(batch['tokens'])
            loss = compute_loss(outputs, batch)
            loss.backward()
            optimizer.step()
            train_loss += float(loss.item())

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch in val_loader:
                outputs = model(batch['tokens'])
                val_loss += float(compute_loss(outputs, batch).item())

        print(
            f'Epoch {epoch + 1}/{EPOCHS} | '
            f'train_loss={train_loss / max(len(train_loader), 1):.4f} | '
            f'val_loss={val_loss / max(len(val_loader), 1):.4f}'
        )

    torch.save({'state_dict': model.state_dict(), 'vocab': vocab}, STRUCTURE_MODEL_PATH)
    print(f'Saved model to {STRUCTURE_MODEL_PATH}')


if __name__ == '__main__':
    main()
