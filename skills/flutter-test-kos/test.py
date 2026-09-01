#!/usr/bin/env python3
"""flutter-test-kos: Dart/Flutter test paketini kosar.

Komut: flutter test   (proje dizininde, cwd=--project)

Cikis kodlari:
  0 = tum testler gecti
  1 = test kaldi veya komut calistirilamadi
  2 = on kosul eksik: flutter yok / --project verilmedi / pubspec.yaml yok /
      test/ altinda *_test.dart yok. Arac veya test yoksa sahte 'pass' uretilmez.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="flutter test sarucusu")
    ap.add_argument("--project", required=True, help="Flutter proje dizini")
    ap.add_argument("--flutter", default="flutter", help="flutter calistirilabilir adi/yolu")
    ap.add_argument("--timeout", type=int, default=600, help="test paketi yavas olabilir")
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

    test_dir = project / "test"
    test_files = list(test_dir.glob("*_test.dart")) if test_dir.is_dir() else []
    if not test_files:
        print(f"ON KOSUL: test/ altinda *_test.dart yok: {project}", file=sys.stderr)
        print("          'All tests passed' uydurmak yerine once test yaz.", file=sys.stderr)
        return 2

    cmd = [exe, "test"]
    try:
        proc = subprocess.run(cmd, cwd=str(project), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"KALDI: {args.timeout}s icinde bitmedi (takilan test?).", file=sys.stderr)
        return 1

    output = (proc.stdout or "") + (proc.stderr or "")

    if proc.returncode != 0:
        print(f"KALDI: flutter test cikis kodu {proc.returncode}", file=sys.stderr)
        for line in output.strip().splitlines()[-25:]:
            print("  " + line, file=sys.stderr)
        return 1

    print(f"GECTI: flutter test temiz ({len(test_files)} test dosyasi)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
