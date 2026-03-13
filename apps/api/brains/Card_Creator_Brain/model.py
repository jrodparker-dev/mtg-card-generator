from torch import nn

class CreatorBrainModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, label_maps):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.encoder = nn.GRU(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        out_dim = hidden_dim * 2

        self.type_head = nn.Linear(out_dim, len(label_maps["primary_type"]))
        self.rarity_head = nn.Linear(out_dim, len(label_maps["rarity"]))
        self.color_head = nn.Linear(out_dim, len(label_maps["color_bucket"]))
        self.mv_head = nn.Linear(out_dim, len(label_maps["mana_value_bucket"]))
        self.trigger_head = nn.Linear(out_dim, len(label_maps["trigger"]))
        self.flags_head = nn.Linear(out_dim, 3)
        self.effects_head = nn.Linear(out_dim, len(label_maps["effects"]))
        self.keywords_head = nn.Linear(out_dim, len(label_maps["keywords"]))

    def encode(self, tokens):
        emb = self.embedding(tokens)
        _, h = self.encoder(emb)
        h = h.transpose(0, 1).reshape(tokens.size(0), -1)
        return h

    def forward(self, tokens):
        h = self.encode(tokens)
        return {
            "primary_type": self.type_head(h),
            "rarity": self.rarity_head(h),
            "color_bucket": self.color_head(h),
            "mana_value_bucket": self.mv_head(h),
            "trigger": self.trigger_head(h),
            "flags": self.flags_head(h),
            "effects": self.effects_head(h),
            "keywords": self.keywords_head(h),
        }
