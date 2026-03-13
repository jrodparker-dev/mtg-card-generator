import torch
from torch import nn


class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, rank: int = 8, alpha: float = 16.0):
        super().__init__()
        self.base = base
        self.rank = rank
        self.alpha = alpha
        self.lora_a = nn.Parameter(torch.zeros(base.in_features, rank))
        self.lora_b = nn.Parameter(torch.zeros(rank, base.out_features))
        nn.init.kaiming_uniform_(self.lora_a, a=5 ** 0.5)
        nn.init.zeros_(self.lora_b)

    def forward(self, x):
        base_out = self.base(x)
        lora_out = x @ self.lora_a @ self.lora_b
        return base_out + lora_out * (self.alpha / self.rank)
