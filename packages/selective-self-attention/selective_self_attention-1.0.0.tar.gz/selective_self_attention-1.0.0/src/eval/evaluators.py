from typing import Any, Dict, Optional

from .metrics import accuracy, mse


class Evaluator:
    """
    Minimal evaluator that computes accuracy or MSE over a dataloader given a model/algo.
    """
    def __init__(self, algorithm: Any, metric: str = 'accuracy') -> None:
        self.algorithm = algorithm
        self.metric = metric.lower()

    def evaluate(self, loader) -> Dict[str, float]:
        agg = {'metric': 0.0, 'count': 0}
        if not loader:
            return agg
        for batch in loader:
            try:
                outputs = self.algorithm.inference(batch.get('inputs'))
                t = batch.get('targets')
                if self.metric == 'accuracy':
                    val = accuracy(outputs, t)
                else:
                    val = mse(outputs, t)
            except Exception:
                val = 0.0
            agg['metric'] += float(val)
            agg['count'] += 1
        if agg['count'] > 0:
            agg['metric'] /= float(agg['count'])
        return agg
