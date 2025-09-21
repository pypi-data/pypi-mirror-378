from typing import Optional, Tuple

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


def clamp_probs(x, eps: float = EPS):
    if torch is None:
        return x
    return torch.clamp(x, eps, 1.0 - eps)


def safe_log(x, eps: float = EPS):
    if torch is None:
        return 0.0
    return torch.log(torch.clamp(x, min=eps))


def reduce_loss(loss, reduction: str = "mean"):
    if torch is None:
        return float(loss) if isinstance(loss, (int, float)) else 0.0
    reduction = (reduction or "mean").lower()
    if reduction == "none":
        return loss
    if reduction == "sum":
        return loss.sum()
    return loss.mean()


def masked_mean(x, mask: Optional[Tensor] = None):
    if torch is None:
        return float(x) if isinstance(x, (int, float)) else 0.0
    if mask is None:
        return x.mean()
    x = x * mask
    denom = torch.clamp(mask.sum(), min=1.0)
    return x.sum() / denom


def nll_from_logits(logits: Tensor, targets: Tensor, reduction: str = "mean"):
    """Numerically stable NLL using log_softmax.
    targets: LongTensor of shape (N,) or (N, ...) class indices.
    """
    if torch is None:
        return 0.0
    logp = F.log_softmax(logits, dim=-1)
    if targets.dim() == logits.dim() - 1:
        # class indices
        loss = -logp.gather(dim=-1, index=targets.unsqueeze(-1)).squeeze(-1)
    else:
        # one-hot or probabilities provided
        loss = -(targets * logp).sum(dim=-1)
    return reduce_loss(loss, reduction)
