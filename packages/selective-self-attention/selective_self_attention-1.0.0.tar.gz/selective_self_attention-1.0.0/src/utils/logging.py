from __future__ import annotations
import logging
from typing import Optional


def get_logger(name: str = 'repro', level: str = 'INFO', propagate: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    lvl = getattr(logging, str(level).upper(), logging.INFO)
    logger.setLevel(lvl)
    ch = logging.StreamHandler()
    ch.setLevel(lvl)
    fmt = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s: %(message)s')
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    logger.propagate = propagate
    return logger
