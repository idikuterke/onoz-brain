#!/usr/bin/env python3
"""godot-test-runner: res://tests/run_tests.gd script'ini headless kosar.

Komut: godot --headless --path <proje> -s res://tests/run_tests.gd
Karar: cikis kodu 0 VE ciktida hata marker'i yok.

Cikis kodlari:
  0 = test script'i temiz kostu
  1 = godot sifirdan dondu veya ciktida hata marker'i bulundu
  2 = on kosul eksik: godot yok / --project verilmedi / gecerli Godot projesi
      degil / test script'i yok. Arac yoksa asla sahte 'pass' uretilmez.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Godot script hatasinda bile exit 0 donebilir; bu yuzden cikti de taranir.
ERROR_MARKERS = ("SCRIPT ERROR", "ERROR:", "Parse Error", "Failed to load",
                 "Assertion failed")


def res_to_fs(project: Path, res_path: str) -> Path:
    rel = res_path[len("res://"):] if res_path.startswith("res://") else res_path
    return project / rel


def main() -> int:
    ap = argparse.ArgumentParser(description="Godot test script'ini headless kosar")
    ap.add_argument("--project", required=True, help="Godot proje dizini")
    ap.add_argument("--script", default="res://tests/run_tests.gd",
                    help="test script'i (res:// yolu)")
    ap.add_argument("--godot", default="godot", help="godot calistirilabilir adi/yolu")
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()

    exe = shutil.which(args.godot)
    if exe is None:
        print(f"ON KOSUL: '{args.godot}' PATH'te bulunamadi.", file=sys.stderr)
        return 2

    project = Path(args.project).expanduser()
    if not (project / "project.godot").exists():
        print(f"ON KOSUL: gecerli Godot projesi degil (project.godot yok): {project}",
              file=sys.stderr)
        return 2

    script_fs = res_to_fs(project, args.script)
    if not script_fs.exists():
        print(f"ON KOSUL: test script'i yok: {script_fs}", file=sys.stderr)
        print("          Test uydurmak yerine once script'i yaz.", file=sys.stderr)
        return 2

    cmd = [exe, "--headless", "--path", str(project), "-s", args.script]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"KALDI: {args.timeout}s icinde bitmedi (muhtemel sonsuz dongu).",
              file=sys.stderr)
        return 1

    output = (proc.stdout or "") + (proc.stderr or "")
    hits = [line for line in output.splitlines() if any(m in line for m in ERROR_MARKERS)]

    if proc.returncode != 0:
        print(f"KALDI: Godot cikis kodu {proc.returncode}", file=sys.stderr)
        for line in hits[:20] or output.strip().splitlines()[-10:]:
            print("  " + line, file=sys.stderr)
        return 1
    if hits:
        print(f"KALDI: cikista {len(hits)} hata satiri (Godot yine de 0 dondu olabilir)",
              file=sys.stderr)
        for line in hits[:20]:
            print("  " + line, file=sys.stderr)
        return 1

    print(f"GECTI: {args.script} temiz kostu (hata marker'i yok)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
