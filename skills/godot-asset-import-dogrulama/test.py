#!/usr/bin/env python3
"""godot-asset-import-dogrulama: headless --import ciktisini kayip resource/acilamayan
asset acisindan tarar.

Komut: godot --headless --path <proje> --import   (Godot 4+; Godot 3'te bu bayrak yok)

Cikis kodlari:
  0 = import temiz, kayip bagimlilik marker'i yok
  1 = godot sifirdan dondu veya ciktida kayip bağımlılık marker'i bulundu
  2 = on kosul eksik: godot yok / --project verilmedi / gecerli Godot projesi degil
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Godot 4 import ciktisinda kayip resource / basarisiz import kaliplari.
MISSING_MARKERS = (
    "Failed to load",
    "Cannot open file",
    "Could not find type",
    "No loader found",
    "Error importing",
    "Parse Error",
    "SCRIPT ERROR",
    "missing dependency",
)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Godot --import ciktisini kayip bagimlilik acisindan dogrular")
    ap.add_argument("--project", required=True, help="Godot proje dizini")
    ap.add_argument("--godot", default="godot", help="godot calistirilabilir adi/yolu")
    ap.add_argument("--timeout", type=int, default=300,
                    help="ilk import uzun surebilir")
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

    cmd = [exe, "--headless", "--path", str(project), "--import"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"KALDI: {args.timeout}s icinde bitmedi.", file=sys.stderr)
        return 1

    output = (proc.stdout or "") + (proc.stderr or "")
    hits = [line for line in output.splitlines() if any(m in line for m in MISSING_MARKERS)]

    if proc.returncode != 0:
        print(f"KALDI: Godot cikis kodu {proc.returncode}", file=sys.stderr)
        # Not: Godot 3'te --import bilinmeyen bayrak oldugu icin buraya duser;
        # ciktiya bakip ayirt et.
        for line in output.strip().splitlines()[-15:]:
            print("  " + line, file=sys.stderr)
        return 1
    if hits:
        print(f"KALDI: import ciktisinda {len(hits)} kayip bagimlilik satiri", file=sys.stderr)
        for line in hits[:20]:
            print("  " + line, file=sys.stderr)
        return 1

    print("GECTI: --import temiz, kayip bagimlilik marker'i yok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
