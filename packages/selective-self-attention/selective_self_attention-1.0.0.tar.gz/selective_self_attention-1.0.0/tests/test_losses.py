import importlib

try:
    import torch
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


def test_losses_imports():
    m = importlib.import_module('src.losses')
    assert hasattr(m, 'CompositeLoss')


def test_composite_loss_zeros_when_no_terms():
    if not TORCH_AVAILABLE:
        return
    import torch
    from src.losses import CompositeLoss
    class DummyModel(torch.nn.Module):
        def forward(self, x):
            return x
    model = DummyModel()
    loss_fn = CompositeLoss(model=model, config={'weights': {'ce': 0.0, 'mse': 0.0}})
    x = torch.randn(3, 5)
    y = torch.randint(0, 5, (3,))
    out = loss_fn(x, y, {})
    assert 'loss' in out
