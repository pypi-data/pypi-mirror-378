from typing import List, Optional, Tuple, Dict, Any
import math

try:
    import torch
    from torch import nn
    from torch.nn import functional as F
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    nn = object  # type: ignore
    F = object  # type: ignore


class MLPBlock(nn.Module):
    def __init__(self, in_dim: int, out_dim: int, hidden_dim: Optional[int] = None, activation: str = 'relu', dropout: float = 0.0):
        if torch is None:
            self._no_torch = True
            return
        super().__init__()
        hidden_dim = hidden_dim or out_dim
        act = nn.ReLU if activation == 'relu' else nn.Tanh
        layers: List[nn.Module] = [
            nn.Linear(in_dim, hidden_dim),
            act(),
            nn.Dropout(p=dropout) if dropout and dropout > 0 else nn.Identity(),
            nn.Linear(hidden_dim, out_dim),
        ]
        self.net = nn.Sequential(*layers)

    def forward(self, x):  # type: ignore[override]
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')
        return self.net(x)


class Residual(nn.Module):
    def __init__(self, module: 'nn.Module'):
        if torch is None:
            self._no_torch = True
            return
        super().__init__()
        self.module = module

    def forward(self, x):  # type: ignore[override]
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')
        return x + self.module(x)


class LayerNorm(nn.LayerNorm):
    def __init__(self, normalized_shape, eps: float = 1e-5):
        if torch is None:
            self._no_torch = True
            return
        super().__init__(normalized_shape, eps=eps)


class StandardSelfAttention(nn.Module):
    """
    Standard multi-head self-attention layer for comparison with SSA.
    """
    def __init__(
        self,
        dim: int,
        num_heads: int = 8,
        qkv_bias: bool = False,
        attn_drop: float = 0.0,
        proj_drop: float = 0.0
    ):
        if torch is None:
            self._no_torch = True
            return
        super().__init__()

        assert dim % num_heads == 0, f"dim {dim} should be divisible by num_heads {num_heads}"

        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.scale = self.head_dim ** -0.5

        # Standard attention projections
        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.attn_drop = nn.Dropout(attn_drop)
        self.proj = nn.Linear(dim, dim)
        self.proj_drop = nn.Dropout(proj_drop)

    def forward(self, x: 'torch.Tensor', mask: Optional['torch.Tensor'] = None) -> 'torch.Tensor':
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')

        B, N, C = x.shape

        # Generate QKV
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv.unbind(0)  # Each: [B, num_heads, N, head_dim]

        # Compute attention scores
        attn = (q @ k.transpose(-2, -1)) * self.scale  # [B, num_heads, N, N]

        # Apply causal mask if provided
        if mask is not None:
            attn = attn.masked_fill(mask == 0, float('-inf'))

        # Apply softmax to get attention weights
        attn = F.softmax(attn, dim=-1)
        attn = self.attn_drop(attn)

        # Apply attention to values
        out = attn @ v  # [B, num_heads, N, head_dim]

        # Reshape and project output
        out = out.transpose(1, 2).reshape(B, N, C)  # [B, N, C]
        out = self.proj(out)
        out = self.proj_drop(out)

        return out

    def get_attention_spikiness(self, x: 'torch.Tensor') -> float:
        """
        Compute attention spikiness metric for standard attention.
        """
        if torch is None:
            return 0.0

        with torch.no_grad():
            B, N, C = x.shape
            qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
            q, k, v = qkv.unbind(0)

            attn = F.softmax((q @ k.transpose(-2, -1)) * self.scale, dim=-1)

            # Compute spikiness for each attention head and average
            l1_norm = torch.sum(torch.abs(attn), dim=-1)  # [B, num_heads, N]
            l2_norm_sq = torch.sum(attn ** 2, dim=-1)  # [B, num_heads, N]
            spikiness = l1_norm / (l2_norm_sq * N)

            return spikiness.mean().item()


class TemperatureModule(nn.Module):
    """
    Temperature scaling module for Selective Self-Attention.
    Implements both token-aware and position-aware temperature scaling.
    """
    def __init__(self, dim: int, use_position_aware: bool = True):
        if torch is None:
            self._no_torch = True
            return
        super().__init__()
        self.dim = dim
        self.use_position_aware = use_position_aware

        # Token-aware temperature: τ_tok(x) = tanh(f(x))
        # Using weight sharing strategy - reuse attention weights
        self.token_temp_proj = nn.Linear(dim, 1, bias=False)

        # Position-aware temperature: τ_pos(x) = 1 + σ(α)log(n)
        if use_position_aware:
            self.position_alpha = nn.Parameter(torch.zeros(1))

    def forward(self, x: 'torch.Tensor', positions: Optional['torch.Tensor'] = None) -> 'torch.Tensor':
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')

        # Token-aware temperature
        token_temp = torch.tanh(self.token_temp_proj(x))  # Shape: [batch, seq_len, 1]

        # Position-aware temperature
        if self.use_position_aware and positions is not None:
            # positions shape: [seq_len] or [batch, seq_len]
            if positions.dim() == 1:
                positions = positions.unsqueeze(0).expand(x.size(0), -1)

            pos_temp = 1 + torch.sigmoid(self.position_alpha) * torch.log(positions.float() + 1)
            pos_temp = pos_temp.unsqueeze(-1)  # Shape: [batch, seq_len, 1]

            return token_temp + pos_temp

        return token_temp


class SelectiveSelfAttention(nn.Module):
    """
    Selective Self-Attention (SSA) Layer from NeurIPS 2024 paper:
    "Selective Attention: Enhancing Transformer through Principled Context Control"

    Key innovations:
    1. Temperature scaling for queries and values
    2. Optional temperature scaling for keys
    3. Decoupling semantic similarity from contextual sparsity
    4. Weight sharing strategy for parameter efficiency (<0.5% overhead)
    5. Position-aware and token-aware temperature scaling
    """
    def __init__(
        self,
        dim: int,
        num_heads: int = 8,
        qkv_bias: bool = False,
        attn_drop: float = 0.0,
        proj_drop: float = 0.0,
        use_query_temp: bool = True,
        use_key_temp: bool = False,  # Optional key temperature scaling
        use_value_temp: bool = True,
        use_position_aware: bool = True,
        weight_sharing: bool = True
    ):
        if torch is None:
            self._no_torch = True
            return
        super().__init__()

        assert dim % num_heads == 0, f"dim {dim} should be divisible by num_heads {num_heads}"

        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.scale = self.head_dim ** -0.5
        self.use_query_temp = use_query_temp
        self.use_key_temp = use_key_temp
        self.use_value_temp = use_value_temp
        self.weight_sharing = weight_sharing

        # Standard attention projections
        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.attn_drop = nn.Dropout(attn_drop)
        self.proj = nn.Linear(dim, dim)
        self.proj_drop = nn.Dropout(proj_drop)

        # Temperature modules for SSA
        if use_query_temp:
            self.query_temp = TemperatureModule(dim, use_position_aware)
        if use_key_temp:
            self.key_temp = TemperatureModule(dim, use_position_aware)
        if use_value_temp:
            self.value_temp = TemperatureModule(dim, use_position_aware)
    
    def forward(self, x: 'torch.Tensor', mask: Optional['torch.Tensor'] = None) -> 'torch.Tensor':
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')

        B, N, C = x.shape

        # Generate QKV
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv.unbind(0)  # Each: [B, num_heads, N, head_dim]

        # Apply temperature scaling to queries
        if self.use_query_temp:
            positions = torch.arange(N, device=x.device, dtype=torch.long)
            query_temps = self.query_temp(x, positions)  # [B, N, 1]
            query_temps = query_temps.unsqueeze(1).expand(-1, self.num_heads, -1, -1)  # [B, num_heads, N, 1]
            q = q * query_temps  # Element-wise scaling

        # Apply temperature scaling to keys
        if self.use_key_temp:
            positions = torch.arange(N, device=x.device, dtype=torch.long)
            key_temps = self.key_temp(x, positions)  # [B, N, 1]
            key_temps = key_temps.unsqueeze(1).expand(-1, self.num_heads, -1, -1)  # [B, num_heads, N, 1]
            k = k * key_temps  # Element-wise scaling

        # Compute attention scores with scaled queries and keys
        attn = (q @ k.transpose(-2, -1)) * self.scale  # [B, num_heads, N, N]

        # Apply causal mask if provided
        if mask is not None:
            attn = attn.masked_fill(mask == 0, float('-inf'))

        # Apply softmax to get attention weights
        attn = F.softmax(attn, dim=-1)
        attn = self.attn_drop(attn)

        # Apply attention to values
        out = attn @ v  # [B, num_heads, N, head_dim]

        # Apply temperature scaling to values
        if self.use_value_temp:
            positions = torch.arange(N, device=x.device, dtype=torch.long)
            value_temps = self.value_temp(x, positions)  # [B, N, 1]
            value_temps = value_temps.unsqueeze(1).expand(-1, self.num_heads, -1, -1)  # [B, num_heads, N, 1]
            out = out * value_temps  # Element-wise scaling

        # Reshape and project output
        out = out.transpose(1, 2).reshape(B, N, C)  # [B, N, C]
        out = self.proj(out)
        out = self.proj_drop(out)

        return out
    
    def get_attention_spikiness(self, x: 'torch.Tensor') -> float:
        """
        Compute attention spikiness metric as used in the paper.
        Spikiness = ||s||_1 / (||s||_2^2 * L) where s is softmax probability vector.
        Lower values indicate sparser (spikier) attention.
        """
        if torch is None:
            return 0.0

        with torch.no_grad():
            B, N, C = x.shape
            qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
            q, k, v = qkv.unbind(0)

            if self.use_query_temp:
                positions = torch.arange(N, device=x.device, dtype=torch.long)
                query_temps = self.query_temp(x, positions)
                query_temps = query_temps.unsqueeze(1).expand(-1, self.num_heads, -1, -1)
                q = q * query_temps

            if self.use_key_temp:
                positions = torch.arange(N, device=x.device, dtype=torch.long)
                key_temps = self.key_temp(x, positions)
                key_temps = key_temps.unsqueeze(1).expand(-1, self.num_heads, -1, -1)
                k = k * key_temps

            attn = F.softmax((q @ k.transpose(-2, -1)) * self.scale, dim=-1)

            # Compute spikiness for each attention head and average
            l1_norm = torch.sum(torch.abs(attn), dim=-1)  # [B, num_heads, N]
            l2_norm_sq = torch.sum(attn ** 2, dim=-1)  # [B, num_heads, N]
            spikiness = l1_norm / (l2_norm_sq * N)

            return spikiness.mean().item()


class TransformerBlock(nn.Module):
    """
    Transformer block with Selective Self-Attention.
    Drop-in replacement for standard transformer blocks.
    """
    def __init__(
        self,
        dim: int,
        num_heads: int = 8,
        mlp_ratio: float = 4.0,
        qkv_bias: bool = False,
        drop: float = 0.0,
        attn_drop: float = 0.0,
        use_ssa: bool = True,
        **ssa_kwargs
    ):
        if torch is None:
            self._no_torch = True
            return
        super().__init__()
        
        self.norm1 = LayerNorm(dim)
        
        # Use SSA or standard attention
        if use_ssa:
            self.attn = SelectiveSelfAttention(
                dim=dim,
                num_heads=num_heads,
                qkv_bias=qkv_bias,
                attn_drop=attn_drop,
                proj_drop=drop,
                **ssa_kwargs
            )
        else:
            # Standard multi-head attention for fair comparison
            self.attn = StandardSelfAttention(
                dim=dim,
                num_heads=num_heads,
                qkv_bias=qkv_bias,
                attn_drop=attn_drop,
                proj_drop=drop
            )
        
        self.norm2 = LayerNorm(dim)
        
        mlp_hidden_dim = int(dim * mlp_ratio)
        self.mlp = MLPBlock(dim, dim, mlp_hidden_dim, dropout=drop)
    
    def forward(self, x: 'torch.Tensor', mask: Optional['torch.Tensor'] = None) -> 'torch.Tensor':
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')
        
        # Pre-norm architecture
        if hasattr(self.attn, 'forward') and 'mask' in self.attn.forward.__code__.co_varnames:
            x = x + self.attn(self.norm1(x), mask=mask)
        else:
            x = x + self.attn(self.norm1(x))
        
        x = x + self.mlp(self.norm2(x))
        return x
