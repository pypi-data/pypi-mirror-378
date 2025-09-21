from typing import Optional
import os


def prepare_dataset(name: str, root: str = 'data', overwrite: bool = False) -> str:
    """
    Placeholder for dataset download / preparation.
    Creates a directory and a marker file indicating readiness.
    """
    dpath = os.path.join(root, name)
    os.makedirs(dpath, exist_ok=True)
    marker = os.path.join(dpath, '_PREPARED')
    if overwrite or not os.path.exists(marker):
        with open(marker, 'w', encoding='utf-8') as f:
            f.write('ok')
    return dpath
