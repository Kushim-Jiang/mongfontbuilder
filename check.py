#!/usr/bin/env python3
"""Unified check entry point for the mongfontbuilder repository.

Runs all linters / type checkers for the Python library and the web docs site:

  - Python  : ruff (lint + format), pyright (type check; CLI equivalent of Pylance)
  - Web     : astro check (TypeScript + .astro), svelte-check (Svelte components)

Usage:
  uv run check.py            # run all checks
  uv run check.py --fix      # auto-fix fixable issues (ruff --fix, ruff format) first
  uv run check.py --json     # also write reports/check.json with per-tool results
  uv run check.py --fast     # skip slow checks (astro check)
  uv run check.py --only ruff,pyright

Exit code is non-zero if any check fails (safe for CI / pre-commit).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent
PY = (
    REPO / ".venv" / "Scripts" / "python.exe"
    if sys.platform == "win32"
    else REPO / ".venv" / "bin" / "python"
)
RUFF = (
    REPO / ".venv" / "Scripts" / "ruff.exe"
    if sys.platform == "win32"
    else REPO / ".venv" / "bin" / "ruff"
)
NPM_BIN = REPO / "node_modules" / ".bin"
RUFF_RULES = "E4,E7,E9,F,I"


def run(label: str, args: list[str], cwd: Path = REPO, timeout: int = 600) -> dict:
    """Run a check command, capturing output. Never raises on non-zero exit."""
    exe = args[0]
    if not (REPO / exe).exists() and not Path(exe).suffix:
        # bare command like "npm" — resolve through the shell on Windows
        args = args  # noqa: PLW0127
    started = time.perf_counter()
    print(f"\n=== {label} ===", flush=True)
    try:
        proc = subprocess.run(
            [str(a) for a in args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        code = proc.returncode
    except FileNotFoundError:
        out, code = f"command not found: {args[0]}", 127
    except subprocess.TimeoutExpired:
        out, code = f"timed out after {timeout}s", 124
    if out.strip():
        print(out.rstrip(), flush=True)
    ok = code == 0
    print(f"--- {label}: {'PASS' if ok else 'FAIL'} (exit={code}) ---", flush=True)
    return {
        "label": label,
        "command": " ".join(map(str, args)),
        "exit": code,
        "ok": ok,
        "seconds": round(time.perf_counter() - started, 2),
    }


def npm(*args: str) -> list[str]:
    """Invoke an npm-bin script cross-platform."""
    if sys.platform == "win32":
        return ["cmd", "/c", str(NPM_BIN / f"{args[0]}.cmd"), *args[1:]]
    return [str(NPM_BIN / args[0]), *args[1:]]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--fix", action="store_true", help="auto-fix fixable issues first (ruff)")
    parser.add_argument("--json", action="store_true", help="write reports/check.json")
    parser.add_argument("--fast", action="store_true", help="skip slow checks (astro check)")
    parser.add_argument(
        "--only", default="", help="comma-separated subset: ruff,ruff-format,pyright,astro,svelte"
    )
    args = parser.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()}

    def wanted(name: str) -> bool:
        return not only or name in only

    results: list[dict] = []

    if args.fix and wanted("ruff"):
        results.append(
            run("ruff --fix", [RUFF, "check", "--select", RUFF_RULES, "--fix", "lib", "tests"])
        )
        results.append(run("ruff format", [RUFF, "format", "lib", "tests"]))

    if wanted("ruff"):
        results.append(run("ruff check", [RUFF, "check", "--select", RUFF_RULES, "lib", "tests"]))
    if wanted("ruff-format"):
        results.append(run("ruff format --check", [RUFF, "format", "--check", "lib", "tests"]))
    if wanted("pyright"):
        results.append(run("pyright", [PY, "-m", "pyright", "lib"]))
    if wanted("astro") and not args.fast:
        results.append(run("astro check", npm("astro", "check"), timeout=900))
    if wanted("svelte"):
        results.append(run("svelte-check", npm("svelte-check", "--output", "human")))

    failed = [r for r in results if not r["ok"]]
    print("\n================ SUMMARY ================", flush=True)
    for r in results:
        print(f"{'PASS' if r['ok'] else 'FAIL'}  {r['label']:<22} ({r['seconds']}s)")
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")

    if args.json:
        report = REPO / "reports" / "check.json"
        report.parent.mkdir(exist_ok=True)
        report.write_text(
            json.dumps({"results": results, "ok": not failed}, indent=2), encoding="utf-8"
        )
        print(f"Report written to {report}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
