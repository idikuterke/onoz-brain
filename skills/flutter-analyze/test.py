#!/usr/bin/env python3
"""flutter-analyze: Dart statik analizini koşar, sorun kalmadığını doğrular.

Komut: flutter analyze   (proje dizininde, cwd=--project)

Cikis kodlari:
  0 = analyze temiz (exit 0)
  1 = analyzer hata/uyari buldu veya komut calistirilamadi
  2 = on kosul eksik: flutter yok / --project verilmedi / pubspec.yaml yok.
      Arac yoksa asla sahte 'pass' uretilmez.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="flutter analyze sarucusu")
    ap.add_argument("--project", required=True, help="Flutter proje dizini")
    ap.add_argument("--flutter", default="flutter", help="flutter calistirilabilir adi/yolu")
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()

    exe = shutil.which(args.flutter)
    if exe is None:
        print(f"ON KOSUL: '{args.flutter}' PATH'te bulunamadi.", file=sys.stderr)
        return 2

    project = Path(args.project).expanduser()
    if not (project / "pubspec.yaml").exists():
        print(f"ON KOSUL: gecerli Flutter projesi degil (pubspec.yaml yok): {project}",
              file=sys.stderr)
        return 2

    cmd = [exe, "analyze"]
    try:
        proc = subprocess.run(cmd, cwd=str(project), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"KALDI: {args.timeout}s icinde bitmedi.", file=sys.stderr)
        return 1

    output = (proc.stdout or "") + (proc.stderr or "")

    if proc.returncode != 0:
        print(f"KALDI: flutter analyze cikis kodu {proc.returncode}", file=sys.stderr)
        for line in output.strip().splitlines()[-25:]:
            print("  " + line, file=sys.stderr)
        return 1

    print("GECTI: flutter analyze temiz")
    return 0


if __name__ == "__main__":
    sys.exit(main())
