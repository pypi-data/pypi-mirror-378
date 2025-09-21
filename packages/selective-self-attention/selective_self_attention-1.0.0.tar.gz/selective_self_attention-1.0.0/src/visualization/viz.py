from typing import Dict, List, Optional

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None  # type: ignore


def plot_metric_curve(history: Dict[str, List[float]], out_path: Optional[str] = None):
    """Plot metric curves from a history dict: {name: [values...]}. Saves if out_path given."""
    if plt is None:
        return None
    fig, ax = plt.subplots(figsize=(6, 4))
    for k, v in history.items():
        ax.plot(v, label=k)
    ax.legend()
    ax.set_xlabel('step')
    ax.set_ylabel('value')
    ax.grid(True)
    if out_path:
        fig.savefig(out_path, bbox_inches='tight')
        plt.close(fig)
        return out_path
    return fig
