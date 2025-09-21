from typing import Any, Optional

try:
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore


class IdentityTransform:
    def __call__(self, x: Any) -> Any:
        return x


class Normalize:
    """
    Normalize tensor inputs with mean and std. If torch is unavailable, acts as identity.
    """
    def __init__(self, mean: float = 0.0, std: float = 1.0) -> None:
        self.mean = float(mean)
        self.std = float(std) if std not in (0, None) else 1.0

    def __call__(self, x: Any) -> Any:
        if torch is None:
            return x
        try:
            return (x - self.mean) / self.std
        except Exception:
            return x
