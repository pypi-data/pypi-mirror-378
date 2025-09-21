# determinismus_kit/cli.py
from __future__ import annotations
import argparse
import runpy
import sys
from .core import deterministic, snapshot_environment

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="determinismus_kit", description="Determinismus-Kit CLI")
    sub = p.add_subparsers(dest="cmd")

    prun = sub.add_parser("run", help="Skript im deterministischen Kontext ausführen")
    prun.add_argument("script", help="Pfad zum Python-Skript (.py)")
    prun.add_argument("script_args", nargs=argparse.REMAINDER, help="Argumente NACH '--' an das Skript weitergeben")
    prun.add_argument("--seed", type=int, default=123, help="Seed für RNGs (default: 123)")
    prun.add_argument("--threads", type=int, default=1, help="Max. Threads für BLAS/OMP (default: 1)")
    prun.add_argument("--snapshot", type=str, default=None, help="Optional: schreibe Umgebungs-Snapshot nach PATH")
    prun.add_argument("--no-cuda-determinism", action="store_true", help="CUDA-Deterministik NICHT erzwingen")
    return p

def _cli_run(args: argparse.Namespace) -> int:
    script = args.script
    if not script:
        print("Fehler: Bitte ein Zielskript angeben (z. B. my_script.py)", file=sys.stderr)
        return 2

    sys_argv_backup = list(sys.argv)
    sys.argv = [script] + (args.script_args or [])

    with deterministic(seed=args.seed, threads=args.threads, force_cuda_determinism=not args.no_cuda_determinism):
        if args.snapshot:
            snapshot_environment(args.snapshot)
            print(f"[Determinismus] Snapshot geschrieben: {args.snapshot}")

        try:
            runpy.run_path(script, run_name="__main__")
        except SystemExit as e:
            code = int(e.code) if isinstance(e.code, int) else 0
            sys.argv = sys_argv_backup
            return code
        except Exception:
            sys.argv = sys_argv_backup
            raise
        finally:
            sys.argv = sys_argv_backup
    return 0

def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "run":
        return _cli_run(args)
    else:
        parser.print_help()
        return 0
