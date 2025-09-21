from typing import Any, Dict

try:
    import torch
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False

from src.algorithms import CoreAlgorithm


class DummyCallableModel:
    def train(self):
        self._mode = 'train'
    def eval(self):
        self._mode = 'eval'
    def __call__(self, x):
        return x


def test_core_algorithm_inference_dummy():
    model = DummyCallableModel()
    algo = CoreAlgorithm(model=model, losses=None, optimizer=None, schedulers=None, config={})
    out = algo.inference({'a': 1})
    assert out == {'a': 1}


def test_core_algorithm_step_if_torch():
    if not TORCH_AVAILABLE:
        return
    import torch
    class Lin(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.l = torch.nn.Linear(4, 3)
        def forward(self, x):
            return self.l(x)
    model = Lin()
    from src.losses import CompositeLoss
    loss = CompositeLoss(model=model, config={'weights': {'ce': 1.0, 'mse': 0.0}})
    optim = torch.optim.SGD(model.parameters(), lr=1e-3)
    algo = CoreAlgorithm(model=model, losses=loss, optimizer=optim, schedulers=None, config={'training': {'amp': False}})
    batch = {'inputs': torch.randn(2,4), 'targets': torch.randint(0,3,(2,))}
    metrics = algo.step(batch)
    assert 'loss' in metrics
