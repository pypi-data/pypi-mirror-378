from typing import Any, Dict, Optional

try:
    import torch
    from torch import nn
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    nn = object  # type: ignore


class LinearHead(nn.Module if hasattr(nn, '__mro__') else object):
    """
    Simple linear projection head for classification/regression.
    """
    def __init__(self, in_dim: int = 32, out_dim: int = 10) -> None:
        if torch is None:
            self._no_torch = True
            return
        super().__init__()
        self.proj = nn.Linear(in_dim, out_dim)

    def forward(self, x):  # type: ignore[override]
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')
        return self.proj(x)


def create_head(config: Optional[Dict[str, Any]] = None) -> LinearHead:
    cfg = (config or {}).get('head', config or {})
    in_dim = int(cfg.get('in_dim', 32))
    out_dim = int(cfg.get('out_dim', 10))
    return LinearHead(in_dim=in_dim, out_dim=out_dim)
