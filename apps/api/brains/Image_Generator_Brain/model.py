import torch
from torch import nn

from .config import IMAGE_SIZE, LATENT_DIM, PROMPT_DIM


class ConditionalArtVAE(nn.Module):
    def __init__(self, vocab_size: int, image_size: int = IMAGE_SIZE, latent_dim: int = LATENT_DIM, prompt_dim: int = PROMPT_DIM):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, prompt_dim, padding_idx=0)
        self.prompt_proj = nn.Sequential(
            nn.Linear(prompt_dim, prompt_dim),
            nn.ReLU(),
            nn.Linear(prompt_dim, prompt_dim),
        )

        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, 4, 2, 1),
            nn.ReLU(),
            nn.Conv2d(32, 64, 4, 2, 1),
            nn.ReLU(),
            nn.Conv2d(64, 128, 4, 2, 1),
            nn.ReLU(),
            nn.Conv2d(128, 256, 4, 2, 1),
            nn.ReLU(),
        )
        enc_size = image_size // 16
        self.flat_dim = 256 * enc_size * enc_size
        self.fc_mu = nn.Linear(self.flat_dim + prompt_dim, latent_dim)
        self.fc_logvar = nn.Linear(self.flat_dim + prompt_dim, latent_dim)

        self.fc_decode = nn.Linear(latent_dim + prompt_dim, self.flat_dim)
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 4, 2, 1),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 4, 2, 1),
            nn.ReLU(),
            nn.ConvTranspose2d(32, 3, 4, 2, 1),
            nn.Tanh(),
        )
        self.enc_size = enc_size
        self.latent_dim = latent_dim

    def encode_prompt(self, token_ids: torch.Tensor) -> torch.Tensor:
        emb = self.embedding(token_ids)
        mask = (token_ids != 0).float().unsqueeze(-1)
        summed = (emb * mask).sum(dim=1)
        denom = mask.sum(dim=1).clamp(min=1.0)
        return self.prompt_proj(summed / denom)

    def encode(self, images: torch.Tensor, token_ids: torch.Tensor):
        cond = self.encode_prompt(token_ids)
        feat = self.encoder(images).flatten(1)
        joined = torch.cat([feat, cond], dim=1)
        return self.fc_mu(joined), self.fc_logvar(joined), cond

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z: torch.Tensor, cond: torch.Tensor):
        feat = self.fc_decode(torch.cat([z, cond], dim=1))
        feat = feat.view(z.size(0), 256, self.enc_size, self.enc_size)
        return self.decoder(feat)

    def forward(self, images: torch.Tensor, token_ids: torch.Tensor):
        mu, logvar, cond = self.encode(images, token_ids)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z, cond)
        return recon, mu, logvar

    @torch.no_grad()
    def generate(self, token_ids: torch.Tensor, batch_size: int = 1):
        cond = self.encode_prompt(token_ids)
        z = torch.randn(batch_size, self.latent_dim, device=token_ids.device)
        return self.decode(z, cond[:batch_size])
