from typing import Any, Dict, Iterable, Optional

try:
    import torch
    from torch.optim import Optimizer
    from torch.nn.utils import clip_grad_norm_
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    Optimizer = object  # type: ignore
    def clip_grad_norm_(*args, **kwargs):  # type: ignore
        return None


def build_optimizer(params: Iterable[Any], config: Optional[Dict[str, Any]] = None) -> Any:
    """Build optimizer from config. Supports 'adam' and 'sgd'."""
    if torch is None:
        raise RuntimeError('build_optimizer requires PyTorch to be installed.')
    cfg = (config or {}).get('optimizer', config or {})
    name = str(cfg.get('name', 'adam')).lower()
    lr = float(cfg.get('lr', 1e-3))
    weight_decay = float(cfg.get('weight_decay', 0.0))
    if name in ('adam', 'adamw'):
        betas = tuple(cfg.get('betas', (0.9, 0.999)))  # type: ignore
        eps = float(cfg.get('eps', 1e-8))
        if name == 'adamw':
            return torch.optim.AdamW(params, lr=lr, betas=betas, eps=eps, weight_decay=weight_decay)
        return torch.optim.Adam(params, lr=lr, betas=betas, eps=eps, weight_decay=weight_decay)
    elif name in ('sgd',):
        momentum = float(cfg.get('momentum', 0.9))
        nesterov = bool(cfg.get('nesterov', False))
        return torch.optim.SGD(params, lr=lr, momentum=momentum, weight_decay=weight_decay, nesterov=nesterov)
    else:
        raise ValueError(f'Unsupported optimizer: {name}')


def build_scheduler(optimizer: Any, config: Optional[Dict[str, Any]] = None) -> Any:
    """Build LR scheduler: supports none, step, cosine, linear_warmup."""
    if torch is None:
        raise RuntimeError('build_scheduler requires PyTorch to be installed.')
    cfg = (config or {}).get('scheduler', config or {})
    name = str(cfg.get('name', 'none')).lower()
    if name in ('none', 'constant', ''):
        class _NoOp:
            def step(self):
                return None
        return _NoOp()
    elif name == 'step':
        step_size = int(cfg.get('step_size', 30))
        gamma = float(cfg.get('gamma', 0.1))
        return torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)
    elif name == 'cosine':
        T_max = int(cfg.get('T_max', 100))
        eta_min = float(cfg.get('eta_min', 0.0))
        return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=T_max, eta_min=eta_min)
    elif name == 'linear_warmup':
        total_steps = int(cfg.get('total_steps', 1000))
        warmup_steps = int(cfg.get('warmup_steps', 100))
        def lr_lambda(step: int):
            if step < warmup_steps:
                return float(step + 1) / float(max(1, warmup_steps))
            return max(0.0, float(total_steps - step) / float(max(1, total_steps - warmup_steps)))
        return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
    else:
        raise ValueError(f'Unsupported scheduler: {name}')


def gradient_clip(model: Any, config: Optional[Dict[str, Any]] = None) -> Optional[float]:
    if torch is None:
        return None
    max_norm = float((config or {}).get('max_grad_norm', 0.0))
    if max_norm and max_norm > 0:
        params = [p for p in model.parameters() if p.grad is not None]
        return float(clip_grad_norm_(params, max_norm))
    return None


def ema_update(model: Any, ema_model: Any, decay: float = 0.999) -> None:
    if torch is None:
        # Best-effort parameter copy without torch ops
        if hasattr(ema_model, 'load_state_dict') and hasattr(model, 'state_dict'):
            ema_model.load_state_dict(model.state_dict())
        return
    with torch.no_grad():
        msd = dict(model.state_dict())
        for k, v in ema_model.state_dict().items():
            if k in msd:
                v.copy_(v * decay + msd[k] * (1.0 - decay))
