import json
from functools import lru_cache
from typing import Any

import torch

from .config import LABEL_MAPS_JSON, MODEL_STATE, TRAINING_META_JSON
from .model import MechanicsBrainModel
from .text_renderer import render_oracle_text


DEFAULT_MAPS = {
    "triggers": ["none", "etb", "attack", "dies", "combat_damage_to_player", "upkeep", "end_step", "activated", "static"],
    "complexities": ["simple", "medium", "complex"],
    "line_counts": ["1", "2", "3+"],
    "keywords": ["flying", "trample", "vigilance", "haste", "deathtouch", "lifelink", "menace", "ward {2}"],
    "effects": ["vanilla", "draw", "damage", "treasure", "token", "lifegain", "removal", "discard", "mill", "ramp", "counters", "loot", "impulse"],
    "subtypes": ["Wizard", "Goblin", "Angel", "Spirit", "Dragon", "Zombie", "Elf", "Knight", "Rogue", "Beast"],
}


def _shell_to_vector(shell: dict[str, Any], subtype_vocab: list[str]) -> torch.Tensor:
    colors = list(shell.get("colors") or []) or ["C"]
    types = list(shell.get("types") or [])
    rarity = shell.get("rarity") or "Common"
    mv = float(shell.get("manaValue", 0) or 0)
    subtypes = set(shell.get("subtypes") or [])

    color_vocab = ["W", "U", "B", "R", "G", "C"]
    type_vocab = ["Creature", "Planeswalker", "Instant", "Sorcery", "Artifact", "Enchantment", "Land", "Battle", "Unknown"]
    rarity_vocab = ["Common", "Uncommon", "Rare", "Mythic"]

    row = []
    row.extend([1.0 if c in colors else 0.0 for c in color_vocab])
    primary_type = types[0] if types else shell.get("primary_type", "Unknown")
    row.extend([1.0 if primary_type == t else 0.0 for t in type_vocab])
    row.extend([1.0 if rarity == r else 0.0 for r in rarity_vocab])
    row.extend([1.0 if s in subtypes else 0.0 for s in subtype_vocab])
    row.extend([
        min(mv, 10.0) / 10.0,
        1.0 if shell.get("is_legendary") else 0.0,
        1.0 if shell.get("needs_pt") else 0.0,
        1.0 if shell.get("needs_loyalty") else 0.0,
    ])
    name = (shell.get("name") or "").lower()
    for token in ["angel", "dragon", "goblin", "elf", "zombie", "wizard", "cathedral", "void"]:
        row.append(1.0 if token in name else 0.0)
    return torch.tensor(row, dtype=torch.float32).unsqueeze(0)


class MechanicsBrainService:
    def __init__(self):
        self.device = torch.device("cpu")
        self.trained = LABEL_MAPS_JSON.exists() and MODEL_STATE.exists() and TRAINING_META_JSON.exists()

        if self.trained:
            self.maps = json.loads(LABEL_MAPS_JSON.read_text(encoding="utf-8"))
            meta = json.loads(TRAINING_META_JSON.read_text(encoding="utf-8"))
            self.model = MechanicsBrainModel(
                input_dim=meta["input_dim"],
                num_triggers=len(self.maps["triggers"]),
                num_complexities=len(self.maps["complexities"]),
                num_line_counts=len(self.maps["line_counts"]),
                num_keywords=len(self.maps["keywords"]),
                num_effects=len(self.maps["effects"]),
            )
            state = torch.load(MODEL_STATE, map_location=self.device)
            self.model.load_state_dict(state)
            self.model.eval()
        else:
            self.maps = DEFAULT_MAPS
            self.model = None

    def _top_multi(self, logits: torch.Tensor, vocab: list[str], threshold: float = 0.45, cap: int = 3) -> list[str]:
        probs = torch.sigmoid(logits).detach().cpu().numpy().tolist()
        pairs = [(v, p) for v, p in zip(vocab, probs) if p >= threshold]
        pairs.sort(key=lambda x: x[1], reverse=True)
        return [v for v, _ in pairs[:cap]]

    def _heuristic_predict(self, shell: dict[str, Any]) -> dict[str, Any]:
        name = (shell.get("name") or "").lower()
        colors = list(shell.get("colors") or [])
        types = list(shell.get("types") or [])
        mv = int(shell.get("manaValue", 0) or 0)

        trigger = "none"
        keywords = []
        effects = []

        if "Creature" in types:
            if "Angel" in shell.get("subtypes", []):
                keywords.append("flying")
            if "Goblin" in shell.get("subtypes", []):
                keywords.append("haste")
                effects.append("treasure")
                trigger = "combat_damage_to_player"
            elif "Dragon" in shell.get("subtypes", []):
                keywords.extend(["flying", "trample"])
                effects.append("damage")
                trigger = "attack"
            elif "Spirit" in shell.get("subtypes", []):
                keywords.append("flying")
                effects.append("draw")
                trigger = "dies"

        if not effects:
            if "R" in colors:
                effects.append("damage")
                trigger = "etb" if "Creature" not in types else trigger or "attack"
            elif "U" in colors:
                effects.append("draw")
                trigger = "etb"
            elif "B" in colors:
                effects.append("discard")
                trigger = "dies" if "Creature" in types else "etb"
            elif "G" in colors:
                effects.append("counters" if "Creature" in types else "ramp")
                trigger = "etb"
            elif "W" in colors:
                effects.append("token" if "Creature" in types else "lifegain")
                trigger = "etb"
            else:
                effects.append("draw")
                trigger = "activated" if "Artifact" in types else "none"

        if not keywords and "Creature" in types and mv >= 4:
            keywords.append("vigilance" if "W" in colors else "trample" if "G" in colors else "menace" if "B" in colors else "haste" if "R" in colors else "flying" if "U" in colors else "")

        keywords = [k for k in keywords if k][:2]
        pred = {
            "trigger": trigger,
            "complexity": "simple" if mv <= 2 else "medium" if mv <= 5 else "complex",
            "lineCount": "2" if keywords else "1",
            "keywords": keywords,
            "effects": effects[:2] or ["vanilla"],
        }
        pred["oracleText"] = render_oracle_text(shell, pred)
        return pred

    def predict(self, shell: dict[str, Any]) -> dict[str, Any]:
        if self.model is None:
            return self._heuristic_predict(shell)

        x = _shell_to_vector(shell, self.maps["subtypes"])
        with torch.no_grad():
            out = self.model(x)
        trigger = self.maps["triggers"][int(out["trigger"].argmax(dim=1).item())]
        complexity = self.maps["complexities"][int(out["complexity"].argmax(dim=1).item())]
        line_count = self.maps["line_counts"][int(out["line_count"].argmax(dim=1).item())]
        keywords = self._top_multi(out["keywords"][0], self.maps["keywords"], threshold=0.4, cap=2)
        effects = self._top_multi(out["effects"][0], self.maps["effects"], threshold=0.45, cap=2) or ["vanilla"]
        pred = {
            "trigger": trigger,
            "complexity": complexity,
            "lineCount": line_count,
            "keywords": keywords,
            "effects": effects,
        }
        pred["oracleText"] = render_oracle_text(shell, pred)
        return pred


@lru_cache(maxsize=1)
def load_mechanics_service() -> MechanicsBrainService:
    return MechanicsBrainService()
