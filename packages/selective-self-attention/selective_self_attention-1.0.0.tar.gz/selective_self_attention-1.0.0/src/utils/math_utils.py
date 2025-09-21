from typing import Optional

try:
    import torch
    from torch import Tensor
    import torch.nn.functional as F
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    Tensor = object  # type: ignore
    class F:  # type: ignore
        @staticmethod
        def log_softmax(x, dim=-1):
            return x

EPS = 1e-8


def logsumexp(x, dim: int = -1, keepdim: bool = False):
    if torch is None:
        return 0.0
    m, _ = torch.max(x, dim=dim, keepdim=True)
    z = m + torch.log(torch.clamp(torch.sum(torch.exp(x - m), dim=dim, keepdim=True), min=EPS))
    return z if keepdim else z.squeeze(dim)


def softmax_stable(x, dim: int = -1):
    if torch is None:
        return x
    x = x - x.max(dim=dim, keepdim=True).values
    return torch.exp(x) / torch.clamp(torch.sum(torch.exp(x), dim=dim, keepdim=True), min=EPS)


def topk_accuracy(logits: Tensor, targets: Tensor, k: int = 1) -> float:
    if torch is None:
        return 0.0
    if logits.ndim == 1:
        logits = logits.unsqueeze(0)
    maxk = max(1, k)
    _, pred = logits.topk(maxk, dim=1, largest=True, sorted=True)
    correct = pred.eq(targets.view(-1, 1).expand_as(pred)).any(dim=1).float().mean()
    return float(correct.item())
