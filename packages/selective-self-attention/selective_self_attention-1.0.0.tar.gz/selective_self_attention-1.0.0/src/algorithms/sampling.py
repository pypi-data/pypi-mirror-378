from typing import Iterable, List, Optional, Sequence
import random


def set_seed(seed: Optional[int] = None) -> None:
    if seed is None:
        return
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except Exception:
        pass
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


def sample_indices(n: int, k: int, replace: bool = False, seed: Optional[int] = None) -> List[int]:
    """
    Sample k indices from range(n). Deterministic with given seed.
    """
    rnd = random.Random(seed)
    if replace:
        return [rnd.randrange(n) for _ in range(k)]
    else:
        return rnd.sample(range(n), k)


def batch_sampler(lengths: Sequence[int], batch_size: int) -> Iterable[List[int]]:
    """
    Simple sequential batch sampler over dataset lengths.
    """
    idx = list(range(len(lengths)))
    for i in range(0, len(idx), batch_size):
        yield idx[i:i+batch_size]
