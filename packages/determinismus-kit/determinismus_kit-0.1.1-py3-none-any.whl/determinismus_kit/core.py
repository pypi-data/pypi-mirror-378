# determinismus_kit/core.py
from __future__ import annotations
import os
import sys
import platform
import random
import pickle
import contextlib
from typing import Dict, Any

try:
    import numpy as _np
except Exception:
    _np = None

try:
    import torch as _torch
except Exception:
    _torch = None


def set_global_seed(seed: int = 42) -> None:
    random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        if _torch.cuda.is_available():
            _torch.cuda.manual_seed_all(seed)


def set_env_for_determinism(seed: int = 42, force_cuda_determinism: bool = True) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(key, "1")
    if force_cuda_determinism:
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")


def set_torch_determinism(enable: bool = True) -> None:
    if _torch is None:
        return
    try:
        _torch.use_deterministic_algorithms(enable)
    except Exception:
        pass
    if _torch.backends and hasattr(_torch.backends, "cudnn"):
        _torch.backends.cudnn.benchmark = False
        _torch.backends.cudnn.deterministic = True


def limit_threads(n: int = 1) -> None:
    n_str = str(max(1, int(n)))
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = n_str


def save_rng_state(path: str) -> None:
    state: Dict[str, Any] = {"random": random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        state["torch_cpu"] = _torch.random.get_rng_state()
        if _torch.cuda.is_available():
            try:
                state["torch_cuda"] = _torch.cuda.get_rng_state_all()
            except Exception:
                pass
    with open(path, "wb") as f:
        pickle.dump(state, f)


def load_rng_state(path: str) -> None:
    with open(path, "rb") as f:
        state = pickle.load(f)
    if "random" in state:
        random.setstate(state["random"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None:
        if "torch_cpu" in state:
            _torch.random.set_rng_state(state["torch_cpu"])
        if "torch_cuda" in state and _torch.cuda.is_available():
            try:
                _torch.cuda.set_rng_state_all(state["torch_cuda"])
            except Exception:
                pass


def snapshot_environment(path: str = "repro_env.json") -> None:
    info: Dict[str, Any] = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "python_implementation": platform.python_implementation(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "env": {
            k: os.environ.get(k) for k in [
                "PYTHONHASHSEED",
                "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS",
                "CUBLAS_WORKSPACE_CONFIG",
                "CUDA_LAUNCH_BLOCKING"
            ] if os.environ.get(k) is not None
        },
        "packages": {}
    }
    try:
        import importlib.metadata as _im
    except Exception:
        _im = None
    if _im is not None:
        try:
            for dist in _im.distributions():
                name = dist.metadata.get("Name") or dist.metadata.get("Summary")
                version = dist.version
                if name:
                    info["packages"][name] = version
        except Exception:
            pass

    with open(path, "w", encoding="utf-8") as f:
        import json as _json
        _json.dump(info, f, ensure_ascii=False, indent=2)


@contextlib.contextmanager
def deterministic(seed: int = 42, threads: int = 1, force_cuda_determinism: bool = True):
    prev_env = {k: os.environ.get(k) for k in (
        "PYTHONHASHSEED", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "CUBLAS_WORKSPACE_CONFIG",
        "CUDA_LAUNCH_BLOCKING"
    )}
    rng_dump_path = None
    try:
        rng_dump_path = "_temp_rng_state.pkl"
        save_rng_state(rng_dump_path)

        set_env_for_determinism(seed=seed, force_cuda_determinism=force_cuda_determinism)
        limit_threads(threads)
        set_global_seed(seed)
        set_torch_determinism(True)

        yield
    finally:
        try:
            if rng_dump_path and os.path.exists(rng_dump_path):
                load_rng_state(rng_dump_path)
                os.remove(rng_dump_path)
        except Exception:
            pass
        for k, v in prev_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        if _torch is not None:
            set_torch_determinism(False)
