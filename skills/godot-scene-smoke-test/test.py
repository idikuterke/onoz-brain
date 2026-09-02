#!/usr/bin/env python3
"""Godot sahnesini headless yukleyip hata ariyor. Cikis 0 = gecti."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ERROR_MARKERS = ("SCRIPT ERROR", "Parse Error", "Failed to load", "Failed loading resource")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--scene", required=True)
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args()

    exe = shutil.which(args.godot)
    if exe is None:
        print(f"HATA: '{args.godot}' PATH'te bulunamadi.", file=sys.stderr)
        return 2

    project = Path(args.project).expanduser()
    if not (project / "project.godot").exists():
        print(f"HATA: gecerli Godot projesi degil: {project}", file=sys.stderr)
        return 2

    cmd = [exe, "--headless", "--quit-after", "2", "--path", str(project), args.scene]
    try:
        proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"HATA: {args.timeout}s icinde bitmedi (muhtemel sonsuz dongu).", file=sys.stderr)
        return 3

    output = (proc.stdout or "") + (proc.stderr or "")
    hits = [line for line in output.splitlines() if any(m in line for m in ERROR_MARKERS)]

    if proc.returncode != 0:
        print(f"KALDI: Godot cikis kodu {proc.returncode}", file=sys.stderr)
        for line in hits[:20]:
            print("  " + line, file=sys.stderr)
        return 1

    if hits:
        print(f"KALDI: {len(hits)} hata satiri bulundu", file=sys.stderr)
        for line in hits[:20]:
            print("  " + line, file=sys.stderr)
        return 1

    print(f"GECTI: {args.scene} temiz yuklendi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
