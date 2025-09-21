from typing import Any, Dict, Iterable, List, Tuple

try:
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore


def default_collate_dict(batch: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Collate a list of dicts with keys 'inputs' and 'targets' into batched tensors if torch is available.
    Otherwise, returns lists.
    """
    b = list(batch)
    inputs = [item.get('inputs') for item in b]
    targets = [item.get('targets') for item in b]
    if torch is not None:
        try:
            inputs = torch.stack(inputs)  # type: ignore[arg-type]
            targets = torch.stack(targets)  # type: ignore[arg-type]
        except Exception:
            pass
    return {'inputs': inputs, 'targets': targets}
