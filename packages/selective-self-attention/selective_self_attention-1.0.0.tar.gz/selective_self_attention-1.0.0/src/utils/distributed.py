from typing import Optional

try:
    import torch
    import torch.distributed as dist
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    class dist:  # type: ignore
        @staticmethod
        def is_available():
            return False

        init_process_group = None
        destroy_process_group = None


def init_distributed(backend: str = 'nccl', init_method: Optional[str] = None, world_size: Optional[int] = None, rank: Optional[int] = None):
    if torch is None or not hasattr(dist, 'is_available') or not dist.is_available():
        return False
    if getattr(dist, 'is_initialized', lambda: False)():
        return True
    kwargs = {}
    if init_method:
        kwargs['init_method'] = init_method
    if world_size is not None:
        kwargs['world_size'] = int(world_size)
    if rank is not None:
        kwargs['rank'] = int(rank)
    try:
        dist.init_process_group(backend=backend, **kwargs)  # type: ignore[arg-type]
        return True
    except Exception:
        return False


def cleanup_distributed():
    if torch is None or not hasattr(dist, 'is_available') or not dist.is_available():
        return
    try:
        dist.destroy_process_group()
    except Exception:
        pass


def get_world_size() -> int:
    if torch is None or not hasattr(dist, 'is_available') or not dist.is_available():
        return 1
    try:
        return dist.get_world_size()  # type: ignore[no-any-return]
    except Exception:
        return 1


def get_rank() -> int:
    if torch is None or not hasattr(dist, 'is_available') or not dist.is_available():
        return 0
    try:
        return dist.get_rank()  # type: ignore[no-any-return]
    except Exception:
        return 0


def is_main_process() -> bool:
    return get_rank() == 0


def barrier():
    if torch is None or not hasattr(dist, 'is_available') or not dist.is_available():
        return
    try:
        dist.barrier()
    except Exception:
        pass
