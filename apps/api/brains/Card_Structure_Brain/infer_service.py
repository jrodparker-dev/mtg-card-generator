import json
from functools import lru_cache

import torch

from .config import STRUCTURE_MODEL_PATH, STRUCTURE_VOCAB_PATH
from .features import encode_name
from .labels import PRIMARY_TYPES, COLOR_BUCKETS, RARITIES, MANA_VALUE_BUCKETS
from .model import CardStructureBrain


class StructureService:
    def __init__(self):
        if STRUCTURE_MODEL_PATH.exists():
            checkpoint = torch.load(STRUCTURE_MODEL_PATH, map_location='cpu')
            vocab = checkpoint['vocab']
            self.model = CardStructureBrain(vocab_size=len(vocab))
            self.model.load_state_dict(checkpoint['state_dict'])
            self.vocab = vocab
            self.model.eval()
            self.trained = True
        elif STRUCTURE_VOCAB_PATH.exists():
            self.vocab = json.loads(STRUCTURE_VOCAB_PATH.read_text(encoding='utf-8'))
            self.model = None
            self.trained = False
        else:
            self.vocab = {'<PAD>': 0, '<UNK>': 1}
            self.model = None
            self.trained = False

    def infer(self, name: str) -> dict:
        if self.model is None:
            return self._heuristic_infer(name)

        tokens = torch.tensor([encode_name(name, self.vocab)], dtype=torch.long)
        with torch.no_grad():
            outputs = self.model(tokens)

        primary_type = PRIMARY_TYPES[int(outputs['primary_type'].argmax(dim=1).item())]
        color_bucket = COLOR_BUCKETS[int(outputs['color_bucket'].argmax(dim=1).item())]
        rarity = RARITIES[int(outputs['rarity'].argmax(dim=1).item())].title()
        mv_bucket = MANA_VALUE_BUCKETS[int(outputs['mana_value_bucket'].argmax(dim=1).item())]
        needs_pt = bool(torch.sigmoid(outputs['needs_pt']).item() >= 0.5)
        needs_loyalty = bool(torch.sigmoid(outputs['needs_loyalty']).item() >= 0.5)
        legendary = bool(torch.sigmoid(outputs['is_legendary']).item() >= 0.5)

        return self._format_output(name, primary_type, color_bucket, rarity, mv_bucket, needs_pt, needs_loyalty, legendary)

    def _heuristic_infer(self, name: str) -> dict:
        lowered = name.lower()
        primary_type = 'Creature'
        if any(word in lowered for word in ['bolt', 'blast', 'ritual', 'command']):
            primary_type = 'Sorcery'
        elif any(word in lowered for word in ['engine', 'relic', 'blade']):
            primary_type = 'Artifact'
        elif any(word in lowered for word in ['cathedral', 'angel', 'priest']):
            primary_type = 'Creature'
        return self._format_output(name, primary_type, 'Colorless', 'Uncommon', '3', primary_type == 'Creature', False, False)

    def _format_output(self, name: str, primary_type: str, color_bucket: str, rarity: str, mv_bucket: str, needs_pt: bool, needs_loyalty: bool, legendary: bool) -> dict:
        if primary_type == 'Creature':
            subtype = 'Wizard'
            if 'goblin' in name.lower():
                subtype = 'Goblin'
            elif 'angel' in name.lower():
                subtype = 'Angel'
            type_line = f"{'Legendary ' if legendary else ''}Creature — {subtype}".strip()
        else:
            type_line = f"{'Legendary ' if legendary else ''}{primary_type}".strip()

        mana_cost = '' if primary_type == 'Land' else self._mana_cost_from_bucket(color_bucket, mv_bucket)

        return {
            'primary_type': primary_type,
            'color_bucket': color_bucket,
            'rarity': rarity,
            'mana_value_bucket': mv_bucket,
            'needs_pt': needs_pt,
            'needs_loyalty': needs_loyalty,
            'is_legendary': legendary,
            'type_line': type_line,
            'mana_cost': mana_cost,
        }

    def _mana_cost_from_bucket(self, color_bucket: str, mv_bucket: str) -> str:
        mana_value = 6 if mv_bucket == '6+' else int(mv_bucket)
        if mana_value == 0:
            return '{0}'
        symbol_map = {
            'W': '{W}', 'U': '{U}', 'B': '{B}', 'R': '{R}', 'G': '{G}',
            'Colorless': '{C}',
        }
        if color_bucket in symbol_map:
            color_symbol = symbol_map[color_bucket]
            generic = max(mana_value - 1, 0)
            return (f'{{{generic}}}' if generic else '') + color_symbol
        return f'{{{mana_value}}}'


@lru_cache(maxsize=1)
def load_structure_service() -> StructureService:
    return StructureService()
