import json

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

from .config import BATCH_SIZE, BETA, EPOCHS, LEARNING_RATE, MODEL_STATE, TRAINING_META_JSON, VOCAB_JSON
from .dataset import ArtDataset, build_vocab, load_rows
from .model import ConditionalArtVAE


def train() -> None:
    rows = load_rows()
    if not rows:
        raise RuntimeError("No image rows found. Run metadata build/download first.")

    vocab = build_vocab(rows)
    ds = ArtDataset(rows, vocab)
    loader = DataLoader(ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)

    device = torch.device("cpu")
    model = ConditionalArtVAE(vocab_size=len(vocab)).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    for epoch in range(EPOCHS):
        running = 0.0
        for images, prompt_ids in loader:
            images = images.to(device)
            prompt_ids = prompt_ids.to(device)

            recon, mu, logvar = model(images, prompt_ids)
            recon_loss = F.mse_loss(recon, images)
            kld = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
            loss = recon_loss + BETA * kld

            opt.zero_grad()
            loss.backward()
            opt.step()
            running += float(loss.item())

        print(f"epoch {epoch + 1}/{EPOCHS} loss={running / max(1, len(loader)):.4f}")

    MODEL_STATE.write_bytes(b"")
    torch.save(model.state_dict(), MODEL_STATE)
    VOCAB_JSON.write_text(json.dumps(vocab, indent=2), encoding="utf-8")
    TRAINING_META_JSON.write_text(json.dumps({"vocab_size": len(vocab)}, indent=2), encoding="utf-8")
    print(f"saved: {MODEL_STATE}")


if __name__ == "__main__":
    train()
