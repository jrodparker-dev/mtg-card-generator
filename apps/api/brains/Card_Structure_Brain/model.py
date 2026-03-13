import torch
from torch import nn

from .labels import PRIMARY_TYPES, COLOR_BUCKETS, RARITIES, MANA_VALUE_BUCKETS


class CardStructureBrain(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 64, hidden_dim: int = 128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.encoder = nn.GRU(embed_dim, hidden_dim, batch_first=True)

        self.primary_type_head = nn.Linear(hidden_dim, len(PRIMARY_TYPES))
        self.color_bucket_head = nn.Linear(hidden_dim, len(COLOR_BUCKETS))
        self.rarity_head = nn.Linear(hidden_dim, len(RARITIES))
        self.mv_head = nn.Linear(hidden_dim, len(MANA_VALUE_BUCKETS))
        self.needs_pt_head = nn.Linear(hidden_dim, 1)
        self.needs_loyalty_head = nn.Linear(hidden_dim, 1)
        self.legendary_head = nn.Linear(hidden_dim, 1)

    def forward(self, tokens: torch.Tensor) -> dict[str, torch.Tensor]:
        x = self.embedding(tokens)
        _, hidden = self.encoder(x)
        h = hidden[-1]
        return {
            'primary_type': self.primary_type_head(h),
            'color_bucket': self.color_bucket_head(h),
            'rarity': self.rarity_head(h),
            'mana_value_bucket': self.mv_head(h),
            'needs_pt': self.needs_pt_head(h).squeeze(-1),
            'needs_loyalty': self.needs_loyalty_head(h).squeeze(-1),
            'is_legendary': self.legendary_head(h).squeeze(-1),
        }
