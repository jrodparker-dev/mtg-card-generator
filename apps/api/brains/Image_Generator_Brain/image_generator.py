import base64
import hashlib
import io
import json
import random
from functools import lru_cache
from pathlib import Path
from typing import Any

import torch
from PIL import Image, ImageDraw, ImageFilter

from .config import EXPORTS_DIR, IMAGE_SIZE, MODEL_STATE, VOCAB_JSON
from .dataset import encode_prompt
from .model import ConditionalArtVAE
from .prompt_builder import build_art_prompt


PALETTES = {
    "W": [(245, 233, 196), (250, 247, 236), (201, 165, 86)],
    "U": [(48, 79, 132), (109, 153, 217), (217, 233, 255)],
    "B": [(33, 22, 45), (91, 57, 124), (196, 172, 224)],
    "R": [(88, 23, 18), (204, 66, 46), (248, 176, 70)],
    "G": [(30, 74, 45), (76, 137, 86), (190, 212, 137)],
    "C": [(37, 52, 66), (86, 123, 136), (188, 215, 216)],
}


def _to_data_uri(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _save_image(img: Image.Image, slug: str) -> str:
    out = EXPORTS_DIR / f"{slug}.png"
    img.save(out)
    return str(out)


def _slugify(text: str) -> str:
    allowed = "".join(ch.lower() if ch.isalnum() else "-" for ch in text.strip())
    slug = "-".join([chunk for chunk in allowed.split("-") if chunk])
    return slug[:64] or "generated-card"


class ImageBrainService:
    def __init__(self):
        self.device = torch.device("cpu")
        self.trained = MODEL_STATE.exists() and VOCAB_JSON.exists()

        if self.trained:
            self.vocab = json.loads(VOCAB_JSON.read_text(encoding="utf-8"))
            self.model = ConditionalArtVAE(vocab_size=len(self.vocab)).to(self.device)
            self.model.load_state_dict(torch.load(MODEL_STATE, map_location=self.device))
            self.model.eval()
        else:
            self.vocab = {"<PAD>": 0, "<UNK>": 1}
            self.model = None

    def _palette(self, card: dict[str, Any]):
        colors = list(card.get("colors") or ["C"])
        return PALETTES.get(colors[0], PALETTES["C"])

    def _procedural_art(self, card: dict[str, Any]) -> Image.Image:
        palette = self._palette(card)
        seed = int(hashlib.sha256((card.get("name") or "card").encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(seed)

        img = Image.new("RGB", (512, 384), palette[0])
        draw = ImageDraw.Draw(img)

        # layered gradient bands
        for y in range(img.height):
            t = y / max(1, img.height - 1)
            c0, c1, c2 = palette
            if t < 0.5:
                s = t / 0.5
                color = tuple(int(c0[i] * (1 - s) + c1[i] * s) for i in range(3))
            else:
                s = (t - 0.5) / 0.5
                color = tuple(int(c1[i] * (1 - s) + c2[i] * s) for i in range(3))
            draw.line((0, y, img.width, y), fill=color)

        # atmospheric circles / magical glows
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        for _ in range(8):
            x = rng.randint(-40, img.width + 40)
            y = rng.randint(-40, img.height + 40)
            r = rng.randint(30, 120)
            color = palette[rng.randint(0, 2)] + (rng.randint(30, 85),)
            gdraw.ellipse((x - r, y - r, x + r, y + r), fill=color)
        glow = glow.filter(ImageFilter.GaussianBlur(radius=25))
        img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
        draw = ImageDraw.Draw(img)

        # foreground silhouette
        horizon = int(img.height * rng.uniform(0.55, 0.72))
        mountain = []
        x = 0
        while x < img.width:
            mountain.append((x, horizon - rng.randint(0, 60)))
            x += rng.randint(20, 60)
        mountain.extend([(img.width, img.height), (0, img.height)])
        draw.polygon(mountain, fill=tuple(max(0, c - 40) for c in palette[0]))

        cx = img.width // 2 + rng.randint(-60, 60)
        cy = img.height // 2 + rng.randint(-20, 30)
        if "Creature" in (card.get("types") or []):
            # abstract figure
            draw.ellipse((cx - 28, cy - 90, cx + 28, cy - 34), fill=tuple(max(0, c - 80) for c in palette[0]))
            draw.rectangle((cx - 22, cy - 34, cx + 22, cy + 60), fill=tuple(max(0, c - 70) for c in palette[0]))
            draw.polygon([(cx - 18, cy + 60), (cx - 48, cy + 130), (cx - 8, cy + 70)], fill=tuple(max(0, c - 75) for c in palette[0]))
            draw.polygon([(cx + 18, cy + 60), (cx + 48, cy + 130), (cx + 8, cy + 70)], fill=tuple(max(0, c - 75) for c in palette[0]))
            if "Angel" in (card.get("subtypes") or []):
                wing = tuple(max(0, c - 30) for c in palette[1])
                draw.polygon([(cx - 20, cy - 20), (cx - 120, cy - 80), (cx - 50, cy + 30)], fill=wing)
                draw.polygon([(cx + 20, cy - 20), (cx + 120, cy - 80), (cx + 50, cy + 30)], fill=wing)
        else:
            # abstract object / spell sigil
            for i in range(5):
                inset = 25 + i * 18
                color = tuple(min(255, c + i * 12) for c in palette[2])
                draw.rounded_rectangle((cx - 110 + inset, cy - 110 + inset, cx + 110 - inset, cy + 110 - inset), radius=16, outline=color, width=4)
            draw.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=palette[2])

        return img.filter(ImageFilter.GaussianBlur(radius=0.5))

    @torch.no_grad()
    def _model_art(self, prompt: str) -> Image.Image:
        token_ids = torch.tensor([encode_prompt(prompt, self.vocab)], dtype=torch.long, device=self.device)
        out = self.model.generate(token_ids, batch_size=1)[0].cpu()
        arr = ((out.clamp(-1, 1) + 1.0) * 127.5).byte().permute(1, 2, 0).numpy()
        return Image.fromarray(arr, mode="RGB").resize((512, 384))

    def generate(self, card: dict[str, Any]) -> dict[str, Any]:
        prompt = build_art_prompt(card)
        slug = _slugify(card.get("name") or "generated-card")
        if self.model is not None:
            try:
                img = self._model_art(prompt)
                mode = "trained-image-brain"
            except Exception:
                img = self._procedural_art(card)
                mode = "procedural-fallback"
        else:
            img = self._procedural_art(card)
            mode = "procedural-fallback"

        path = _save_image(img, slug)
        return {
            "art_prompt": prompt,
            "art_path": path,
            "art_data_uri": _to_data_uri(img),
            "generator_mode": mode,
        }


@lru_cache(maxsize=1)
def load_image_service() -> ImageBrainService:
    return ImageBrainService()
