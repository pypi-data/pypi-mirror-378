# determinismus_kit/cli.py
from __future__ import annotations
import argparse, runpy, sys
from .core import deterministic, snapshot_environment

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="determinismus_kit", description="Determinismus-Kit CLI")
    sub = p.add_subparsers(dest="cmd")

    prun = sub.add_parser("run", help="Skript oder Code im deterministischen Kontext ausführen")
    prun.add_argument("script", nargs="?", help="Pfad zum Python-Skript (.py). Entfällt bei -c/--code.")
    prun.add_argument("-c", "--code", type=str, help="Python-Code direkt ausführen (statt Datei).")
    prun.add_argument("script_args", nargs=argparse.REMAINDER,
                      help="Argumente NACH '--' an Script/Code weitergeben")
    prun.add_argument("--seed", type=int, default=123, help="Seed für RNGs (default: 123)")
    prun.add_argument("--threads", type=int, default=1, help="Max. Threads für BLAS/OMP (default: 1)")
    prun.add_argument("--snapshot", type=str, default=None, help="Optional: schreibe Umgebungs-Snapshot nach PATH")
    prun.add_argument("--no-cuda-determinism", action="store_true", help="CUDA-Deterministik NICHT erzwingen")
    return p

def _cli_run(args: argparse.Namespace) -> int:
    if not args.code and not args.script:
        print("Fehler: Entweder -c/--code ODER eine Script-Datei angeben.", file=sys.stderr)
        return 2

    sys_argv_backup = list(sys.argv)
    target_label = "-c" if args.code else (args.script or "")
    sys.argv = [target_label] + (args.script_args or [])

    with deterministic(seed=args.seed, threads=args.threads, force_cuda_determinism=not args.no_cuda_determinism):
        if args.snapshot:
            snapshot_environment(args.snapshot)
            print(f"[Determinismus] Snapshot geschrieben: {args.snapshot}")

        try:
            if args.code:
                # Führe Code wie ein __main__-Modul aus
                exec(args.code, {"__name__": "__main__"})
            else:
                runpy.run_path(args.script, run_name="__main__")
        except SystemExit as e:
            code = int(e.code) if isinstance(e.code, int) else 0
            sys.argv = sys_argv_backup
            return code
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
