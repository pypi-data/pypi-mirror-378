import importlib

try:
    import torch
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


def test_eval_imports():
    m = importlib.import_module('src.eval')
    assert hasattr(m, 'accuracy')


def test_accuracy_metric():
    from src.eval.metrics import accuracy
    y_true = [0, 1, 2, 2]
    y_pred = [0, 1, 1, 2]
    acc = accuracy(y_true, y_pred)
    assert 0.0 <= acc <= 1.0
