
"""
Losses package placeholder. Paper-specific losses to be implemented.
"""
from typing import Any, Dict

from .main_losses import CompositeLoss  # noqa: F401
from .auxiliary_losses import AuxiliaryLosses, l2_regularization, entropy_loss_from_logits  # noqa: F401


class DummyLoss:
    """
    A minimal composite-like loss that returns zero to keep the pipeline runnable.
    Replace with paper-specific losses.
    """
    def __call__(self, outputs: Any, targets: Any, batch: Dict[str, Any]) -> Dict[str, Any]:
        return {'loss': 0.0}

__all__ = ['DummyLoss', 'CompositeLoss', 'AuxiliaryLosses', 'l2_regularization', 'entropy_loss_from_logits']
