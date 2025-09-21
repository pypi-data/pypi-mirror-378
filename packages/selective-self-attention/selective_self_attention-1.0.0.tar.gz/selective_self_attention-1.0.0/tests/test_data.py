import importlib

try:
    import torch
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


def test_data_imports():
    m = importlib.import_module('src.data')
    assert hasattr(m, 'collate_basic')


def test_tensor_dataset_if_torch():
    if not TORCH_AVAILABLE:
        return
    import torch
    from src.data.datasets import SimpleTensorDataset
    x = torch.randn(5, 4)
    y = torch.randint(0, 2, (5,))
    ds = SimpleTensorDataset(x, y)
    item = ds[0]
    assert 'inputs' in item and 'targets' in item
