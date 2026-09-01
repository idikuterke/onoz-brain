#!/usr/bin/env python3
"""web-build-dogrulama: web projesinin production build'ini koşar.

Komut: npm run build   (proje dizininde, cwd=--project)

Cikis kodlari:
  0 = build temiz (exit 0)
  1 = build kaldi veya komut calistirilamadi
  2 = on kosul eksik: npm yok / --project verilmedi / package.json yok /
      bozuk JSON / 'build' script'i tanimli degil. Arac yoksa sahte 'pass' uretilmez.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="npm run build sarucusu")
    ap.add_argument("--project", required=True, help="web proje dizini (package.json kok)")
    ap.add_argument("--npm", default="npm", help="npm calistirilabilir adi/yolu")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    exe = shutil.which(args.npm)
    if exe is None:
        print(f"ON KOSUL: '{args.npm}' PATH'te bulunamadi.", file=sys.stderr)
        return 2

    project = Path(args.project).expanduser()
    pj = project / "package.json"
    if not pj.exists():
        print(f"ON KOSUL: package.json yok: {project}", file=sys.stderr)
        return 2

    try:
        scripts = json.loads(pj.read_text(encoding="utf-8")).get("scripts", {}) or {}
    except (json.JSONDecodeError, OSError) as exc:
        print(f"ON KOSUL: package.json okunamadi/bozuk: {exc}", file=sys.stderr)
        return 2

    if "build" not in scripts:
        print("ON KOSUL: package.json'da 'build' script'i tanimli degil.", file=sys.stderr)
        print("          'build' diye bir script uydurulmaz; once script'i yaz.", file=sys.stderr)
        return 2

    cmd = [exe, "run", "build"]
    try:
        proc = subprocess.run(cmd, cwd=str(project), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"KALDI: {args.timeout}s icinde bitmedi.", file=sys.stderr)
        return 1

    output = (proc.stdout or "") + (proc.stderr or "")

    if proc.returncode != 0:
        print(f"KALDI: npm run build cikis kodu {proc.returncode}", file=sys.stderr)
        for line in output.strip().splitlines()[-25:]:
            print("  " + line, file=sys.stderr)
        return 1

    print("GECTI: npm run build temiz")
    return 0


if __name__ == "__main__":
    sys.exit(main())
