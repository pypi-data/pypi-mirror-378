
"""
Eval package: metrics, evaluators, tables, figures.
"""
from .metrics import accuracy, mse  # noqa: F401
from .evaluators import Evaluator  # noqa: F401
from .tables import build_results_table  # noqa: F401
from .figures import plot_training_curve  # noqa: F401

__all__ = ['accuracy', 'mse', 'Evaluator', 'build_results_table', 'plot_training_curve']
