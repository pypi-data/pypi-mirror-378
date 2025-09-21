from __future__ import annotations
from typing import Any, Dict, Iterable, Optional

from ..utils.logging import get_logger
from ..utils.checkpoint import save_checkpoint
from .seeding import set_seed

try:
    import torch
    from torch.utils.data import DataLoader
except Exception:
    torch = None  # type: ignore
    DataLoader = object  # type: ignore


class Trainer:
    def __init__(self, algorithm: Any, train_loader: Any, val_loader: Optional[Any] = None, config: Optional[Dict[str, Any]] = None) -> None:
        self.algorithm = algorithm
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config or {}
        self.logger = get_logger('Trainer')
        self.epochs = int(self.config.get('training', {}).get('epochs', 1))
        self.log_interval = int(self.config.get('training', {}).get('log_interval', 10))
        self.seed = self.config.get('seed')
        set_seed(self.seed)

    def _iter_loader(self, loader: Any) -> Iterable:
        return loader if loader is not None else []

    def fit(self) -> Dict[str, Any]:
        self.logger.info('Starting training for %d epochs', self.epochs)
        global_step = 0
        last_metrics: Dict[str, Any] = {}
        for epoch in range(1, self.epochs + 1):
            self.logger.info('Epoch %d/%d', epoch, self.epochs)
            for i, batch in enumerate(self._iter_loader(self.train_loader), start=1):
                try:
                    metrics = self.algorithm.step(batch)
                except Exception as e:
                    self.logger.error('Step failed: %s', e)
                    raise
                last_metrics = metrics
                global_step += 1
                if (i % self.log_interval) == 0:
                    self.logger.info('step=%d, metrics=%s', global_step, {k: (float(v) if isinstance(v, (int, float)) else str(v)) for k, v in metrics.items()})
            # Validation hook
            if self.val_loader is not None:
                self.logger.info('Running validation...')
                _ = self.validate()
        self.logger.info('Training complete.')
        return last_metrics

    def validate(self) -> Dict[str, Any]:
        self.logger.info('Validation loop start.')
        agg: Dict[str, float] = {}
        n = 0
        for batch in self._iter_loader(self.val_loader):
            try:
                # Inference can be extended with eval metrics
                _ = self.algorithm.inference(batch.get('inputs'))
            except Exception:
                pass
            n += 1
        self.logger.info('Validation loop end.')
        return agg
