import json

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

from .config import BATCH_SIZE, EPOCHS, EMBED_DIM, HIDDEN_DIM, LEARNING_RATE, LABEL_MAPS_JSON, MODEL_STATE, TRAINING_META_JSON, VOCAB_JSON
from .dataset import CreatorBrainDataset, build_label_maps, build_vocab, load_rows
from .model import CreatorBrainModel

def train():
    rows = load_rows()
    if not rows:
        raise RuntimeError("No creator dataset rows found. Run build_dataset.py first.")

    vocab = build_vocab(rows)
    label_maps = build_label_maps(rows)
    ds = CreatorBrainDataset(rows, vocab, label_maps)
    loader = DataLoader(ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)

    device = torch.device("cpu")
    model = CreatorBrainModel(len(vocab), EMBED_DIM, HIDDEN_DIM, label_maps).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    for epoch in range(EPOCHS):
        total = 0.0
        for batch in loader:
            tokens = batch["tokens"].to(device)
            out = model(tokens)

            loss = 0.0
            for key in ["primary_type", "rarity", "color_bucket", "mana_value_bucket", "trigger"]:
                loss = loss + F.cross_entropy(out[key], batch["single"][key].to(device))
            loss = loss + F.binary_cross_entropy_with_logits(out["flags"], batch["flags"].to(device))
            loss = loss + F.binary_cross_entropy_with_logits(out["effects"], batch["multi"]["effects"].to(device))
            loss = loss + F.binary_cross_entropy_with_logits(out["keywords"], batch["multi"]["keywords"].to(device))

            opt.zero_grad()
            loss.backward()
            opt.step()
            total += float(loss.item())

        print(f"epoch {epoch + 1}/{EPOCHS} loss={total / max(1, len(loader)):.4f}")

    torch.save(model.state_dict(), MODEL_STATE)
    VOCAB_JSON.write_text(json.dumps(vocab, indent=2), encoding="utf-8")
    LABEL_MAPS_JSON.write_text(json.dumps(label_maps, indent=2), encoding="utf-8")
    TRAINING_META_JSON.write_text(json.dumps({
        "vocab_size": len(vocab),
        "embed_dim": EMBED_DIM,
        "hidden_dim": HIDDEN_DIM,
    }, indent=2), encoding="utf-8")
    print(f"saved model to {MODEL_STATE}")

if __name__ == "__main__":
    train()
