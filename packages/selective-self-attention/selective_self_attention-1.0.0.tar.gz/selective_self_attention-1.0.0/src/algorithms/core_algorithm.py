from typing import Any, Dict, Optional

try:
    import torch
    from torch import nn
    from torch.nn import functional as F  # noqa: F401
except Exception:  # pragma: no cover - allow import without torch installed
    torch = None  # type: ignore
    nn = object  # type: ignore


class CoreAlgorithm:
    """
    Generic core algorithm scaffold.
    - step(batch): one training/optimization iteration
    - inference(inputs): forward pass / decoding per paper
    This will be specialized once the paper details are provided.
    """

    def __init__(
        self,
        model: Any,
        losses: Optional[Any] = None,
        optimizer: Optional[Any] = None,
        schedulers: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.model = model
        self.losses = losses
        self.optimizer = optimizer
        self.schedulers = schedulers
        self.config = config or {}

        # AMP support flag
        self._use_amp = bool(self.config.get('training', {}).get('amp', False))
        self._grad_accum = int(self.config.get('training', {}).get('grad_accumulate', 1))
        self._global_step = 0

        # Lazy scaler if torch is available
        self._scaler = None
        if self._use_amp and torch is not None:
            try:
                self._scaler = torch.cuda.amp.GradScaler()
            except Exception:
                self._scaler = None

    def step(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        """
        One algorithmic iteration over a batch.
        Expects batch like {'inputs': X, 'targets': Y, ...}.
        Returns metrics dict including loss if available.
        """
        if hasattr(self.model, 'train'):
            try:
                self.model.train()
            except Exception:
                pass

        inputs = batch.get('inputs')
        targets = batch.get('targets')

        # Forward pass (with optional AMP)
        if self._use_amp and torch is not None and self._scaler is not None:
            with torch.cuda.amp.autocast():
                outputs = self.model(inputs)
                loss_value, loss_dict = self._compute_loss(outputs, targets, batch)
        else:
            outputs = self.model(inputs)
            loss_value, loss_dict = self._compute_loss(outputs, targets, batch)

        metrics: Dict[str, Any] = {**loss_dict}

        # Optimization step if optimizer provided
        if self.optimizer is not None:
            if torch is None:
                raise RuntimeError('Optimizer step requested but PyTorch is not available.')

            is_accum_step = (self._grad_accum > 1) and (self._global_step % self._grad_accum != self._grad_accum - 1)

            if self._use_amp and self._scaler is not None:
                self._scaler.scale(loss_value).backward()
                if not is_accum_step:
                    self._scaler.step(self.optimizer)
                    self._scaler.update()
                    self.optimizer.zero_grad(set_to_none=True)
            else:
                loss_value.backward()
                if not is_accum_step:
                    self.optimizer.step()
                    self.optimizer.zero_grad(set_to_none=True)

            # Step schedulers if provided and not accumulating
            if self.schedulers is not None and not is_accum_step:
                try:
                    if isinstance(self.schedulers, (list, tuple)):
                        for sch in self.schedulers:
                            sch.step()
                    else:
                        self.schedulers.step()
                except Exception:
                    pass

            self._global_step += 1

        # Attach simple diagnostics
        metrics.setdefault('loss', float(loss_dict.get('loss', 0.0) if isinstance(loss_dict.get('loss'), (int, float)) else getattr(loss_value, 'item', lambda: 0.0)()))
        return metrics

    def inference(self, inputs: Any) -> Any:
        """
        Inference/decoding path. Can be replaced with paper-specific decoding.
        """
        if hasattr(self.model, 'eval'):
            try:
                self.model.eval()
            except Exception:
                pass
        return self.model(inputs)

    # Internal utilities
    def _compute_loss(self, outputs: Any, targets: Any, batch: Dict[str, Any]) -> Any:
        """
        Computes loss using provided loss module if available,
        otherwise returns zero loss (detached).
        """
        if self.losses is None:
            if torch is None:
                # Fallback numeric loss value when torch isn't available
                class _Num:
                    def backward(self):
                        raise RuntimeError('Backward not supported without torch.')

                    def item(self):
                        return 0.0

                return _Num(), {'loss': 0.0}
            else:
                return (0.0 if outputs is None else getattr(outputs, 'sum', lambda: 0.0)() * 0.0), {'loss': 0.0}

        # Assume loss module returns a dict with 'loss' key
        loss_out = self.losses(outputs, targets, batch) if callable(self.losses) else self.losses.forward(outputs, targets, batch)
        if isinstance(loss_out, dict):
            loss_value = loss_out.get('loss')
            return loss_value, loss_out
        return loss_out, {'loss': loss_out}


def apply_algorithmic_step(state: Dict[str, Any], inputs: Any) -> Dict[str, Any]:
    """
    Placeholder for algorithmic sub-steps (e.g., inner loop updates, projections).
    Mirrors the paper's pseudocode steps.
    """
    state = dict(state) if state is not None else {}
    state['last_inputs_shape'] = getattr(inputs, 'shape', None)
    return state


def update_rules(params: Any, grads: Any, lr: float = 1e-3) -> None:
    """
    Generic parameter update rule (e.g., gradient descent).
    If torch is available and params are tensors, performs in-place update.
    """
    if torch is None:
        raise RuntimeError('update_rules requires PyTorch to manipulate parameters.')
    with torch.no_grad():
        for p, g in zip(params, grads):
            if g is None:
                continue
            p.add_( -lr * g )
