from typing import Any, Dict, List, Optional

try:
    import torch
    from torch import nn
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    nn = object  # type: ignore


class SimpleBackbone(nn.Module if hasattr(nn, '__mro__') else object):
    """
    Minimal MLP backbone to allow end-to-end testing.
    If PyTorch isn't available, instantiation will raise on forward.
    """
    def __init__(self, input_dim: int = 16, hidden_dims: Optional[List[int]] = None, activation: str = 'relu') -> None:
        if torch is None:
            # Allow construction but clearly fail when used
            self._no_torch = True
            return
        super().__init__()
        hidden_dims = hidden_dims or [32, 32]
        dims = [input_dim] + hidden_dims
        layers: List[nn.Module] = []
        act = nn.ReLU if activation == 'relu' else nn.Tanh
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i+1]))
            layers.append(act())
        self.net = nn.Sequential(*layers)

    def forward(self, x):  # type: ignore[override]
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')
        return self.net(x)


def create_backbone(config: Optional[Dict[str, Any]] = None) -> SimpleBackbone:
    cfg = (config or {}).get('model', config or {})
    input_dim = int(cfg.get('input_dim', 16))
    hidden_dims = cfg.get('hidden_dims', [32, 32])
    activation = str(cfg.get('activation', 'relu'))
    return SimpleBackbone(input_dim=input_dim, hidden_dims=hidden_dims, activation=activation)
