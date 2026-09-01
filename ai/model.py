import math
import torch
from torch import nn

class TinyGPT(nn.Module):
    """A small causal Transformer trained from random weights for MC Dev AI."""
    def __init__(self, vocab_size=256, block_size=256, d_model=192, n_head=6, n_layer=6, dropout=0.1):
        super().__init__()
        self.block_size = block_size
        self.token = nn.Embedding(vocab_size, d_model)
        self.pos = nn.Embedding(block_size, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_head, dim_feedforward=4*d_model,
            dropout=dropout, activation="gelu", batch_first=True, norm_first=True
        )
        self.blocks = nn.TransformerEncoder(layer, num_layers=n_layer)
        self.norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        self.lm_head.weight = self.token.weight
        self.apply(self._init)

    def _init(self, module):
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if isinstance(module, nn.Linear) and module.bias is not None:
                nn.init.zeros_(module.bias)

    def forward(self, idx, targets=None):
        _, t = idx.shape
        if t > self.block_size:
            idx = idx[:, -self.block_size:]
            if targets is not None:
                targets = targets[:, -self.block_size:]
            t = self.block_size
        positions = torch.arange(t, device=idx.device).unsqueeze(0)
        x = self.token(idx) + self.pos(positions)
        mask = torch.triu(torch.ones(t, t, device=idx.device, dtype=torch.bool), diagonal=1)
        x = self.blocks(x, mask=mask)
        logits = self.lm_head(self.norm(x))
        loss = None
        if targets is not None:
            loss = nn.functional.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens=160, temperature=0.75, top_k=40):
        self.eval()
        for _ in range(max_new_tokens):
            context = idx[:, -self.block_size:]
            logits, _ = self(context)
            logits = logits[:, -1, :] / max(temperature, 1e-4)
            if top_k:
                values, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < values[:, [-1]]] = -float("inf")
            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, next_token), dim=1)
        return idx
