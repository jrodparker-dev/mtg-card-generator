import json
from functools import lru_cache

import torch

from .config import LABEL_MAPS_JSON, MODEL_STATE, TRAINING_META_JSON, VOCAB_JSON
from .dataset import encode_tokens, tokenize
from .model import CreatorBrainModel

def _multi(logits, labels, threshold=0.45, cap=3):
    probs = torch.sigmoid(logits).detach().cpu().tolist()
    items = [(label, p) for label, p in zip(labels, probs) if p >= threshold]
    items.sort(key=lambda x: x[1], reverse=True)
    return [label for label, _ in items[:cap]]

class CreatorBrainService:
    def __init__(self):
        self.trained = all(p.exists() for p in [MODEL_STATE, VOCAB_JSON, LABEL_MAPS_JSON, TRAINING_META_JSON])
        if self.trained:
            self.vocab = json.loads(VOCAB_JSON.read_text(encoding="utf-8"))
            self.label_maps = json.loads(LABEL_MAPS_JSON.read_text(encoding="utf-8"))
            meta = json.loads(TRAINING_META_JSON.read_text(encoding="utf-8"))
            self.model = CreatorBrainModel(meta["vocab_size"], meta["embed_dim"], meta["hidden_dim"], self.label_maps)
            self.model.load_state_dict(torch.load(MODEL_STATE, map_location="cpu"))
            self.model.eval()
        else:
            self.vocab = {"<PAD>": 0, "<UNK>": 1}
            self.label_maps = {
                "primary_type": ["Creature", "Artifact", "Instant", "Sorcery", "Enchantment", "Land", "Planeswalker"],
                "rarity": ["Common", "Uncommon", "Rare", "Mythic"],
                "color_bucket": ["W", "U", "B", "R", "G", "Colorless", "W/U", "U/B", "B/R", "R/G", "W/B", "W/R", "U/R", "U/G", "B/G", "W/G"],
                "mana_value_bucket": ["0", "1", "2", "3", "4", "5", "6+"],
                "trigger": ["none", "etb", "attack", "dies", "combat_damage_to_player", "upkeep", "activated", "static"],
                "effects": ["vanilla", "draw", "damage", "treasure", "token", "lifegain", "removal", "discard", "mill", "ramp", "counters", "impulse"],
                "keywords": ["flying", "trample", "vigilance", "haste", "deathtouch", "lifelink", "menace", "ward", "flash", "reach"],
            }
            self.model = None

    def _heuristic(self, name: str):
        low = name.lower()
        primary_type = "Creature"
        rarity = "Uncommon"
        color_bucket = "Colorless"
        mv = "3"
        trigger = "none"
        effects = ["vanilla"]
        keywords = []

        mappings = [
            ("angel", ("Creature", "Mythic", "W", "5", "etb", ["token", "lifegain"], ["flying", "vigilance"])),
            ("dragon", ("Creature", "Rare", "R", "5", "attack", ["damage"], ["flying", "trample"])),
            ("goblin", ("Creature", "Uncommon", "R", "2", "combat_damage_to_player", ["treasure"], ["haste"])),
            ("witch", ("Creature", "Rare", "B", "3", "activated", ["discard"], [])),
            ("archivist", ("Creature", "Rare", "U", "3", "etb", ["draw"], [])),
            ("engine", ("Artifact", "Rare", "Colorless", "4", "activated", ["ramp"], [])),
            ("cathedral", ("Enchantment", "Rare", "W", "4", "upkeep", ["token"], [])),
            ("void", ("Sorcery", "Rare", "B", "4", "none", ["discard", "mill"], [])),
            ("storm", ("Instant", "Uncommon", "U/R", "2", "none", ["draw", "damage"], ["flash"])),
            ("forest", ("Land", "Common", "G", "0", "none", ["ramp"], [])),
        ]
        for token, values in mappings:
            if token in low:
                primary_type, rarity, color_bucket, mv, trigger, effects, keywords = values
                break

        if low.startswith(("lord ", "king ", "queen ", "emperor ", "saint ")):
            rarity = "Mythic"

        return {
            "primary_type": primary_type,
            "rarity": rarity,
            "color_bucket": color_bucket,
            "mana_value_bucket": mv,
            "trigger": trigger,
            "needs_pt": primary_type == "Creature",
            "needs_loyalty": primary_type == "Planeswalker",
            "is_legendary": rarity == "Mythic" and primary_type in {"Creature", "Planeswalker"},
            "effects": effects,
            "keywords": keywords,
        }

    def predict_concept(self, name: str):
        if self.model is None:
            return self._heuristic(name)

        ids = torch.tensor([encode_tokens(tokenize(name), self.vocab)], dtype=torch.long)
        with torch.no_grad():
            out = self.model(ids)

        flags = torch.sigmoid(out["flags"][0]).tolist()
        concept = {
            "primary_type": self.label_maps["primary_type"][int(out["primary_type"].argmax(dim=1).item())],
            "rarity": self.label_maps["rarity"][int(out["rarity"].argmax(dim=1).item())],
            "color_bucket": self.label_maps["color_bucket"][int(out["color_bucket"].argmax(dim=1).item())],
            "mana_value_bucket": self.label_maps["mana_value_bucket"][int(out["mana_value_bucket"].argmax(dim=1).item())],
            "trigger": self.label_maps["trigger"][int(out["trigger"].argmax(dim=1).item())],
            "needs_pt": flags[0] >= 0.5,
            "needs_loyalty": flags[1] >= 0.5,
            "is_legendary": flags[2] >= 0.5,
            "effects": _multi(out["effects"][0], self.label_maps["effects"]),
            "keywords": _multi(out["keywords"][0], self.label_maps["keywords"], threshold=0.40),
        }

        if concept["primary_type"] == "Creature":
            concept["needs_pt"] = True
        if concept["primary_type"] == "Planeswalker":
            concept["needs_loyalty"] = True
        return concept

@lru_cache(maxsize=1)
def load_creator_service():
    return CreatorBrainService()
