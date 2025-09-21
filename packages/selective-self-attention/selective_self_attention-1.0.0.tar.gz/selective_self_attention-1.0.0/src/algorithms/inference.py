from typing import Any, Callable, List, Tuple


def simple_inference(model: Any, inputs: Any) -> Any:
    """
    Basic forward inference helper.
    """
    if hasattr(model, 'eval'):
        try:
            model.eval()
        except Exception:
            pass
    return model(inputs)


def beam_search(
    start_state: Any,
    step_fn: Callable[[Any], Tuple[List[Any], List[float]]],
    beam_width: int = 5,
    max_steps: int = 50,
) -> Tuple[Any, float]:
    """
    Generic beam search scaffold using a user-provided step_fn.
    step_fn(state) -> (next_states, log_probs)
    Returns best (state, score).
    """
    beams: List[Tuple[Any, float]] = [(start_state, 0.0)]
    for _ in range(max_steps):
        new_beams: List[Tuple[Any, float]] = []
        for state, score in beams:
            next_states, logps = step_fn(state)
            for ns, lp in zip(next_states, logps):
                new_beams.append((ns, score + float(lp)))
        new_beams.sort(key=lambda x: x[1], reverse=True)
        beams = new_beams[:beam_width]
    return beams[0]
