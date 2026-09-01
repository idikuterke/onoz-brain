#!/usr/bin/env python3
"""pytest-kos: Python test paketini koşar.

Komut: pytest -q   (proje dizininde, cwd=--project)
pytest PATH'te yoksa fallback: <python> -m pytest -q

Cikis kodlari:
  0 = tum testler gecti
  1 = test kaldi
  2 = on kosul eksik: pytest bulunamadi (fallback da yok) / --project verilmedi /
      projede test dosyasi veya pytest konfigurasyonu yok / pytest test toplayamadi
      (exit 5). Arac yoksa sahte 'pass' uretilmez.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

MARKERS = ("pyproject.toml", "setup.py", "setup.cfg", "pytest.ini", "tox.ini")


def has_tests(project: Path) -> bool:
    if (project / "tests").is_dir():
        return True
    for pat in ("test_*.py", "*_test.py"):
        if any(project.rglob(pat)):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="pytest -q sarucusu")
    ap.add_argument("--project", required=True, help="Python proje dizini")
    ap.add_argument("--python", default=sys.executable,
                    help="fallback icin python yorumlayicisi")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    project = Path(args.project).expanduser()
    if not project.is_dir():
        print(f"ON KOSUL: proje dizini yok: {project}", file=sys.stderr)
        return 2

    configured = any((project / m).exists() for m in MARKERS)
    if not (configured or has_tests(project)):
        print(f"ON KOSUL: projede test dosyasi/pytest konfigurasyonu bulunamadi: {project}",
              file=sys.stderr)
        print("          Test yokken 'gecti' üretilmez; once test yaz.", file=sys.stderr)
        return 2

    exe = shutil.which("pytest")
    if exe is not None:
        cmd = [exe, "-q"]
        kaynak = "PATH'teki pytest"
    else:
        cmd = [args.python, "-m", "pytest", "-q"]
        kaynak = f"'{args.python} -m pytest' (fallback)"

    try:
        proc = subprocess.run(cmd, cwd=str(project), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"KALDI: {args.timeout}s icinde bitmedi (takilan test?).", file=sys.stderr)
        return 1

    output = (proc.stdout or "") + (proc.stderr or "")

    if "No module named pytest" in output:
        print(f"ON KOSUL: pytest kurulu degil ({kaynak} calistirildi).", file=sys.stderr)
        print("          'pip install pytest' gerekli; simule edilmez.", file=sys.stderr)
        return 2
    if proc.returncode == 5:
        print("ON KOSUL: pytest test toplayamadi (exit 5 = no tests ran).", file=sys.stderr)
        for line in output.strip().splitlines()[-10:]:
            print("  " + line, file=sys.stderr)
        return 2
    if proc.returncode != 0:
        print(f"KALDI: pytest cikis kodu {proc.returncode}", file=sys.stderr)
        for line in output.strip().splitlines()[-25:]:
            print("  " + line, file=sys.stderr)
        return 1

    summary = output.strip().splitlines()[-1] if output.strip() else ""
    print(f"GECTI: pytest temiz ({kaynak}) {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
