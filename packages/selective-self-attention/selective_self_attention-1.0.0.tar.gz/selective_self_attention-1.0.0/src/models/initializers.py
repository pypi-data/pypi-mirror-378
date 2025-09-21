from typing import Optional

try:
    import torch
    from torch import nn
    import torch.nn.init as init
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    nn = object  # type: ignore
    class init:  # type: ignore
        @staticmethod
        def xavier_uniform_(w):
            return None


def apply_initialization(module, method: str = 'xavier_uniform', bias: Optional[float] = 0.0):
    if torch is None:
        return module
    m = method.lower() if method else 'xavier_uniform'
    if isinstance(module, (nn.Linear, nn.Conv1d, nn.Conv2d, nn.Conv3d)):
        if m in ('xavier_uniform', 'xavier_uniform_'):
            init.xavier_uniform_(module.weight)
        elif m in ('xavier_normal', 'xavier_normal_'):
            init.xavier_normal_(module.weight)
        elif m in ('kaiming_uniform', 'he_uniform', 'kaiming_uniform_'):
            init.kaiming_uniform_(module.weight, nonlinearity='relu')
        elif m in ('kaiming_normal', 'he_normal', 'kaiming_normal_'):
            init.kaiming_normal_(module.weight, nonlinearity='relu')
        else:
            init.xavier_uniform_(module.weight)
        if getattr(module, 'bias', None) is not None and bias is not None:
            nn.init.constant_(module.bias, float(bias))
    elif isinstance(module, nn.Embedding):
        if m in ('xavier_uniform', 'xavier_uniform_'):
            init.xavier_uniform_(module.weight)
        else:
            init.normal_(module.weight, mean=0.0, std=0.02)
    elif isinstance(module, nn.LayerNorm):
        if getattr(module, 'bias', None) is not None and bias is not None:
            nn.init.constant_(module.bias, float(bias))
        if getattr(module, 'weight', None) is not None:
            nn.init.ones_(module.weight)
    return module


def init_model(model, config: Optional[dict] = None):
    if torch is None:
        return model
    cfg = config or {}
    method = str(cfg.get('method', 'xavier_uniform'))
    bias = cfg.get('bias', 0.0)

    def _init(m):
        apply_initialization(m, method=method, bias=bias)

    model.apply(_init)
    return model
