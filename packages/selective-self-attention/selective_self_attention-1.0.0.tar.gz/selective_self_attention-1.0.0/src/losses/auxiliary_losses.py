from typing import Any, Dict, Optional

try:
    import torch
    from torch import nn
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    nn = object  # type: ignore


def l2_regularization(model: Any, weight: float = 0.0):
    if weight <= 0:
        return 0.0 if torch is None else torch.tensor(0.0)
    if torch is None:
        return 0.0
    reg = torch.tensor(0.0, device=next(model.parameters()).device) if hasattr(model, 'parameters') else torch.tensor(0.0)
    if hasattr(model, 'parameters'):
        for p in model.parameters():
            if p is not None:
                reg = reg + p.pow(2).sum()
    return reg * float(weight)


def entropy_loss_from_logits(logits, weight: float = 0.0, reduction: str = 'mean'):
    if weight <= 0:
        return 0.0 if torch is None else torch.tensor(0.0)
    if torch is None:
        return 0.0
    probs = torch.softmax(logits, dim=-1)
    ent = -(probs * torch.clamp(probs, min=1e-8).log()).sum(dim=-1)
    if reduction == 'sum':
        ent = ent.sum()
    else:
        ent = ent.mean()
    return ent * float(weight)


class AuxiliaryLosses:
    """Container to compute enabled auxiliary losses from a config.
    config example:
    { 'l2_weight': 1e-4, 'entropy_weight': 0.0 }
    """
    def __init__(self, model: Any = None, config: Optional[Dict[str, Any]] = None) -> None:
        self.model = model
        cfg = config or {}
        self.l2_weight = float(cfg.get('l2_weight', 0.0))
        self.entropy_weight = float(cfg.get('entropy_weight', 0.0))

    def __call__(self, outputs, batch):
        total = 0.0 if torch is None else torch.tensor(0.0, device=outputs.device if hasattr(outputs, 'device') else None)
        terms: Dict[str, Any] = {}
        if self.l2_weight > 0 and self.model is not None:
            l2 = l2_regularization(self.model, self.l2_weight)
            terms['aux_l2'] = l2
            total = total + l2
        if self.entropy_weight > 0 and outputs is not None:
            ent = entropy_loss_from_logits(outputs, self.entropy_weight)
            terms['aux_entropy'] = ent
            total = total + ent
        terms['aux_total'] = total
        return terms
