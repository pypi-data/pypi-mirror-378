from __future__ import annotations
from typing import Optional
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
        try:
            import torch.backends.cudnn as cudnn
            cudnn.deterministic = True
            cudnn.benchmark = False
        except Exception:
            pass
    except Exception:
        pass
