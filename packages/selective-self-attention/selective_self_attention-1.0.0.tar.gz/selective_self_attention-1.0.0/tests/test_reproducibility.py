from src.trainers.seeding import set_seed
import random

try:
    import numpy as np
    NP = True
except Exception:
    NP = False


def test_set_seed_python_random():
    set_seed(123)
    a = random.random()
    set_seed(123)
    b = random.random()
    assert a == b


def test_set_seed_numpy():
    if not NP:
        return
    import numpy as np
    set_seed(123)
    a = np.random.rand()
    set_seed(123)
    b = np.random.rand()
    assert a == b
