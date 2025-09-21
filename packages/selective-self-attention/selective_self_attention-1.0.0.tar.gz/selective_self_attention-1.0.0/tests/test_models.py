import importlib
import types

try:
    import torch
    from torch import nn
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


def test_models_imports():
    m = importlib.import_module('src.models')
    assert hasattr(m, 'create_backbone')
    assert hasattr(m, 'create_head')


def test_backbone_head_forward_if_torch():
    if not TORCH_AVAILABLE:
        return
    from src.models import create_backbone, create_head
    import torch
    cfg = {
        'model': {'input_dim': 8, 'hidden_dims': [16]},
        'head': {'in_dim': 16, 'out_dim': 4},
    }
    backbone = create_backbone(cfg)
    head = create_head({'head': {'in_dim': 16, 'out_dim': 4}})
    model = nn.Sequential(backbone, head)
    x = torch.randn(2, 8)
    y = model(x)
    assert y.shape == (2, 4)
}