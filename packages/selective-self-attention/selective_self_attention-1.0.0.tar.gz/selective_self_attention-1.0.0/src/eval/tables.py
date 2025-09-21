from typing import Any, Dict, List


def build_results_table(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a simple summary table (as dict) from a list of run dicts with keys like 'name' and 'metric'.
    """
    table = {'columns': ['name', 'metric'], 'rows': []}
    for r in runs:
        table['rows'].append([r.get('name', 'run'), r.get('metric', 0.0)])
    return table
