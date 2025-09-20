import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Optional, Sequence

from tqdm import tqdm

from jbag import logger


def parallel_map(fn,
                 processes: int,
                 starargs: Optional[Sequence[tuple]] = (),
                 starkwargs: Optional[Sequence[dict]] = (),
                 mp_context_method: Optional[str] = None,
                 show_progress_bar: bool = True):
    """
    Run parallel processing using concurrent ProcessPoolExecutor.
    Args:
        fn (function): function to run.
        processes (int): number of parallel processes.
        starargs (sequence[tuple], optional, default=()): argument groups passed to `fn`.
        starkwargs (sequence[dict], optional, default=()): keyword-arguments passed to `fn`.
        mp_context_method (string, optional, default=None): multiprocessing context ('fork', 'spawn', 'forkserver', or None).
        show_progress_bar (bool, optional, default=True): whether to show progress bar.

    Returns:

    """
    if not mp_context_method in ["fork", "spawn", "forkserver", None]:
        raise ValueError(
            f"Unsupported multiprocessing context: {mp_context_method}. Supported: fork, spawn, forkserver, or None.")

    n_starargs = len(starargs)
    n_starkwds = len(starkwargs)
    if n_starargs == 0 and n_starkwds > 0:
        starargs = [()] * n_starkwds
    elif n_starkwds == 0 and n_starargs > 0:
        starkwargs = [{}] * n_starkwds
    elif n_starargs != n_starkwds:
        raise ValueError("Mismatched number of starargs and number of starkwargs.")

    max_procs = mp.cpu_count()
    requested_procs = processes
    processes = min(processes, max_procs, len(starargs) or 1)
    if processes < requested_procs:
        logger.warn(f"Adjusted processes to {processes} (CPU limit or task count).")

    mp_context = mp.get_context(mp_context_method) if mp_context_method else None
    results = []
    with ProcessPoolExecutor(max_workers=processes, mp_context=mp_context) as executor:
        features = [executor.submit(fn, *args, **kwargs) for args, kwargs in zip(starargs, starkwargs)]

        with tqdm(total=len(starargs), disable=not show_progress_bar) as pbar:
            for future in as_completed(features):
                results.append(future.result())
                pbar.update()
    return results
