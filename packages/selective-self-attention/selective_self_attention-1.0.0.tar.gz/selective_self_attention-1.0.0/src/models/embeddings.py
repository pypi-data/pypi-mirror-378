from typing import Optional
import math

try:
    import torch
    from torch import nn
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    nn = object  # type: ignore


class SinusoidalPositionalEncoding(nn.Module):
    def __init__(self, dim: int, max_len: int = 5000):
        if torch is None:
            self._no_torch = True
            return
        super().__init__()
        pe = torch.zeros(max_len, dim)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, dim, 2).float() * (-math.log(10000.0) / dim))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, L, D)
        self.register_buffer('pe', pe, persistent=False)

    def forward(self, x):  # type: ignore[override]
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')
        L = x.size(1)
        return x + self.pe[:, :L]


class PositionalEncoding(nn.Module):
    """
    Positional encoding compatible with SSA transformer.
    Returns positional encodings for a given sequence length.
    """
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        if torch is None:
            self._no_torch = True
            return
        super().__init__()
        
        self.dropout = nn.Dropout(dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                            (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        # Register as buffer (not parameter)
        self.register_buffer('pe', pe)
    
    def forward(self, seq_len: int) -> 'torch.Tensor':
        """
        Args:
            seq_len: Length of the sequence
            
        Returns:
            Positional encoding tensor of shape [seq_len, d_model]
        """
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')
        
        return self.pe[:seq_len]


class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size: int, dim: int):
        if torch is None:
            self._no_torch = True
            return
        super().__init__()
        self.emb = nn.Embedding(vocab_size, dim)

    def forward(self, x):  # type: ignore[override]
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')
        return self.emb(x)


def create_embeddings(config: Optional[dict] = None):
    cfg = config or {}
    typ = str(cfg.get('type', 'token')).lower()
    if typ == 'token':
        return TokenEmbedding(int(cfg.get('vocab_size', 1000)), int(cfg.get('dim', 32)))
    elif typ in ('pos', 'positional', 'sinusoidal'):
        return SinusoidalPositionalEncoding(int(cfg.get('dim', 32)), int(cfg.get('max_len', 5000)))
    else:
        raise ValueError(f'Unknown embedding type: {typ}')
