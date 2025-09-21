from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping, Optional, Union
import os
import json

try:
    import yaml  # type: ignore
except Exception:
    yaml = None  # type: ignore

ConfigLike = Union[Dict[str, Any], Mapping[str, Any]]


def merge_dicts(base: ConfigLike, update: ConfigLike) -> Dict[str, Any]:
    out: Dict[str, Any] = dict(base)
    for k, v in (update or {}).items():
        if k in out and isinstance(out[k], dict) and isinstance(v, Mapping):
            out[k] = merge_dicts(out[k], v)
        else:
            out[k] = v
    return out


def _load_yaml(path: str) -> Dict[str, Any]:
    if yaml is None:
        # Fallback: try json
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def load_config(paths: Union[str, Iterable[str]], overrides: Optional[ConfigLike] = None) -> Dict[str, Any]:
    if isinstance(paths, str):
        paths = [paths]
    cfg: Dict[str, Any] = {}
    for p in paths:
        if p and os.path.isfile(p):
            part = _load_yaml(p)
            cfg = merge_dicts(cfg, part)
    if overrides:
        cfg = merge_dicts(cfg, overrides)
    return cfg
