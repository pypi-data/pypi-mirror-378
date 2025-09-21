from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple

try:
    import torch
    from torch.utils.data import Dataset, TensorDataset
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    class Dataset:  # type: ignore
        pass
    class TensorDataset:  # type: ignore
        pass


class SimpleDataset(Dataset if hasattr(Dataset, '__mro__') else object):
    """
    A minimal dataset wrapping lists or tensors into dicts with keys 'inputs' and 'targets'.
    """
    def __init__(self, inputs: Any, targets: Any, transform: Optional[Callable] = None):
        self.inputs = inputs
        self.targets = targets
        self.transform = transform
        self._length = len(inputs) if hasattr(inputs, '__len__') else 0

    def __len__(self):  # type: ignore[override]
        return self._length

    def __getitem__(self, idx):  # type: ignore[override]
        x = self.inputs[idx]
        y = self.targets[idx]
        if self.transform is not None:
            x = self.transform(x)
        return {'inputs': x, 'targets': y}


def build_tensor_dataset(n: int = 64, input_dim: int = 16, num_classes: int = 10):
    """
    Build a small synthetic dataset for smoke tests.
    Returns a TensorDataset if torch is available; otherwise, a list-based SimpleDataset.
    """
    if torch is None:
        import random
        inputs = [[random.random() for _ in range(input_dim)] for __ in range(n)]
        targets = [random.randrange(num_classes) for __ in range(n)]
        return SimpleDataset(inputs, targets)
    x = torch.randn(n, input_dim)
    y = torch.randint(0, num_classes, (n,))
    return TensorDataset(x, y)
