from __future__ import annotations
from typing import Any, Dict, Optional

try:
    import torch
except Exception:
    torch = None  # type: ignore


class EarlyStopping:
    def __init__(self, patience: int = 10, minimize: bool = True):
        self.patience = patience
        self.minimize = minimize
        self.best: Optional[float] = None
        self.bad_epochs = 0
        self.should_stop = False

    def step(self, metric: float) -> None:
        if self.best is None:
            self.best = metric
            self.bad_epochs = 0
            return
        improved = metric < self.best if self.minimize else metric > self.best
        if improved:
            self.best = metric
            self.bad_epochs = 0
        else:
            self.bad_epochs += 1
            if self.bad_epochs >= self.patience:
                self.should_stop = True


class LRSchedulerStep:
    def __init__(self, scheduler: Any):
        self.scheduler = scheduler

    def step(self):
        try:
            self.scheduler.step()
        except Exception:
            pass


class EMACallback:
    def __init__(self, model: Any, decay: float = 0.999):
        self.decay = decay
        self.ema_model = None
        if hasattr(model, 'state_dict') and hasattr(model, 'load_state_dict'):
            # Shallow copy via state dict clone-like behavior
            import copy
            self.ema_model = copy.deepcopy(model)
            if torch is not None:
                for p in self.ema_model.parameters():
                    p.requires_grad_(False)
        self._model_ref = model

    def update(self):
        try:
            if self.ema_model is None:
                return
            if torch is None:
                self.ema_model.load_state_dict(self._model_ref.state_dict())
                return
            with torch.no_grad():
                msd = dict(self._model_ref.state_dict())
                for k, v in self.ema_model.state_dict().items():
                    if k in msd:
                        v.copy_(v * self.decay + msd[k] * (1.0 - self.decay))
        except Exception:
            pass


class CheckpointCallback:
    def __init__(self, save_fn, path: str, monitor: Optional[str] = 'loss', minimize: bool = True):
        self.save_fn = save_fn
        self.path = path
        self.monitor = monitor
        self.minimize = minimize
        self.best: Optional[float] = None

    def step(self, metrics: Dict[str, Any], model: Any = None, optimizer: Any = None, scheduler: Any = None):
        val = None if self.monitor is None else metrics.get(self.monitor)
        if val is None:
            return
        if self.best is None or ((val < self.best) if self.minimize else (val > self.best)):
            self.best = float(val)
            try:
                self.save_fn(self.path, model=model, optimizer=optimizer, scheduler=scheduler, extra={'best_metric': self.best})
            except Exception:
                pass
