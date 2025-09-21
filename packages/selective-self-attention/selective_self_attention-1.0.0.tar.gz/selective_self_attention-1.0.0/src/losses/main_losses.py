from typing import Any, Dict, Optional

try:
    import torch
    from torch import nn
    import torch.nn.functional as F
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    nn = object  # type: ignore

from .metrics_loss_utils import nll_from_logits, reduce_loss
from .auxiliary_losses import AuxiliaryLosses


class CompositeLoss:
    """
    Composite loss: supports CE (from logits) and MSE, plus auxiliary terms.
    Config example:
      {
        'weights': { 'ce': 1.0, 'mse': 0.0 },
        'reduction': 'mean',
        'aux': { 'l2_weight': 0.0, 'entropy_weight': 0.0 }
      }
    """
    def __init__(self, model: Any = None, config: Optional[Dict[str, Any]] = None) -> None:
        cfg = config or {}
        self.weights = dict(cfg.get('weights', {'ce': 1.0, 'mse': 0.0}))
        self.reduction = str(cfg.get('reduction', 'mean')).lower()
        self.aux = AuxiliaryLosses(model=model, config=(cfg.get('aux') or {}))

    def _ce_loss(self, logits, targets):
        if torch is None:
            return 0.0
        if targets.dtype in (torch.long, torch.int64):
            return nll_from_logits(logits, targets, reduction=self.reduction)
        else:
            # treat as one-hot / probabilities
            logp = F.log_softmax(logits, dim=-1)
            loss = -(targets * logp).sum(dim=-1)
            return reduce_loss(loss, self.reduction)

    def _mse_loss(self, preds, targets):
        if torch is None:
            return 0.0
        loss = (preds - targets) ** 2
        return reduce_loss(loss, self.reduction)

    def __call__(self, outputs: Any, targets: Any, batch: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # If torch unavailable, return zeros
        if torch is None:
            return {'loss': 0.0}

        total = torch.tensor(0.0, device=outputs.device if hasattr(outputs, 'device') else None)
        terms: Dict[str, Any] = {}

        w_ce = float(self.weights.get('ce', 0.0))
        w_mse = float(self.weights.get('mse', 0.0))

        if w_ce > 0:
            ce = self._ce_loss(outputs, targets)
            terms['loss_ce'] = ce
            total = total + w_ce * ce
        if w_mse > 0:
            mse = self._mse_loss(outputs, targets)
            terms['loss_mse'] = mse
            total = total + w_mse * mse

        # Auxiliary terms (depend on outputs/model)
        aux_terms = self.aux(outputs, batch or {})
        terms.update(aux_terms)
        if 'aux_total' in aux_terms:
            total = total + aux_terms['aux_total']

        terms['loss'] = total
        return terms
