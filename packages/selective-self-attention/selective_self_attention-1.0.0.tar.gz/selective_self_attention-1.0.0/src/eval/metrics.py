from typing import Any, Dict

try:
    import torch
    import torch.nn.functional as F
except Exception:  # pragma: no cover
    torch = None  # type: ignore


def accuracy(logits, targets) -> float:
    if torch is None:
        return 0.0
    if targets.dtype not in (torch.long, torch.int64):
        targets = targets.argmax(dim=-1)
    preds = logits.argmax(dim=-1)
    return float((preds == targets).float().mean().item())


def mse(preds, targets) -> float:
    if torch is None:
        return 0.0
    return float(((preds - targets) ** 2).mean().item())
