from typing import Any, Dict, List, Optional


def plot_training_curve(history: List[Dict[str, Any]], out_path: Optional[str] = None) -> Dict[str, Any]:
    ""
    Minimal plotting stub that returns x/y arrays instead of writing files.
    If matplotlib is available and out_path is provided, it will save a PNG.
    ""
    xs = list(range(1, len(history) + 1))
    ys = [float(h.get('loss', 0.0)) for h in history]
    result = {'x': xs, 'y': ys}
    try:
        import matplotlib.pyplot as plt  # type: ignore
        if out_path:
            plt.figure()
            plt.plot(xs, ys)
            plt.xlabel('step')
            plt.ylabel('loss')
            plt.title('Training Curve')
            plt.savefig(out_path)
            plt.close()
            result['saved'] = out_path
    except Exception:
        pass
    return result
