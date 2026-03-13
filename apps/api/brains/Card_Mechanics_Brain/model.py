import torch
from torch import nn

from .config import DROPOUT, HIDDEN_DIM


class MechanicsBrainModel(nn.Module):
    def __init__(self, input_dim: int, num_triggers: int, num_complexities: int, num_line_counts: int, num_keywords: int, num_effects: int):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Linear(input_dim, HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(HIDDEN_DIM, HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
        )
        self.trigger_head = nn.Linear(HIDDEN_DIM, num_triggers)
        self.complexity_head = nn.Linear(HIDDEN_DIM, num_complexities)
        self.line_count_head = nn.Linear(HIDDEN_DIM, num_line_counts)
        self.keyword_head = nn.Linear(HIDDEN_DIM, num_keywords)
        self.effect_head = nn.Linear(HIDDEN_DIM, num_effects)

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        h = self.backbone(x)
        return {
            "trigger": self.trigger_head(h),
            "complexity": self.complexity_head(h),
            "line_count": self.line_count_head(h),
            "keywords": self.keyword_head(h),
            "effects": self.effect_head(h),
            "embedding": h,
        }
