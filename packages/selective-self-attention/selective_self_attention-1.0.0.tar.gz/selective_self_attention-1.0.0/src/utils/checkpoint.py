from __future__ import annotations
from typing import Any, Dict, Optional
import os
import json
import pickle

try:
    import torch
except Exception:
    torch = None  # type: ignore


def _ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def save_checkpoint(path: str, model: Any = None, optimizer: Any = None, scheduler: Any = None, extra: Optional[Dict[str, Any]] = None) -> None:
    state: Dict[str, Any] = dict(extra or {})
    if model is not None:
        try:
            state['model'] = model.state_dict()
        except Exception:
            state['model'] = None
    if optimizer is not None:
        try:
            state['optimizer'] = optimizer.state_dict()
        except Exception:
            state['optimizer'] = None
    if scheduler is not None:
        try:
            state['scheduler'] = scheduler.state_dict()
        except Exception:
            state['scheduler'] = None

    _ensure_dir(path)
    if torch is not None:
        try:
            torch.save(state, path)
            return
        except Exception:
            pass
    # Fallback to pickle if torch not available
    with open(path, 'wb') as f:
        pickle.dump(state, f)


def load_checkpoint(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    if torch is not None:
        try:
            return torch.load(path, map_location='cpu')
        except Exception:
            pass
    with open(path, 'rb') as f:
        return pickle.load(f)
