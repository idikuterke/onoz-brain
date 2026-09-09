#!/usr/bin/env python3
"""ProjectSettings ve EditorBuildSettings icindeki sahne yollarinin gecerliligini denetler."""
from pathlib import Path
import re
import sys

def main() -> int:
    pv = Path("ProjectSettings/ProjectVersion.txt")
    if not pv.exists():
        print("KALDI: ProjectSettings/ProjectVersion.txt bulunamadi.", file=sys.stderr)
        return 1
    text = pv.read_text(encoding="utf-8", errors="replace")
    if "m_EditorVersion:" not in text:
        print("KALDI: ProjectVersion.txt icinde m_EditorVersion tanimi yok.", file=sys.stderr)
        return 1

    eb = Path("ProjectSettings/EditorBuildSettings.asset")
    if not eb.exists():
        print("KALDI: ProjectSettings/EditorBuildSettings.asset bulunamadi.", file=sys.stderr)
        return 1

    eb_text = eb.read_text(encoding="utf-8", errors="replace")
    scenes = re.findall(r"path:\s*(Assets/[^\r\n]+)", eb_text)
    if not scenes:
        print("KALDI: EditorBuildSettings.asset icinde sahne tanimi bulunamadi.", file=sys.stderr)
        return 1

    missing = [s for s in scenes if not Path(s).exists()]
    if missing:
        print(f"KALDI: {len(missing)} build sahnesi diskte bulunamadi:", file=sys.stderr)
        for s in missing:
            print(f"  - {s}", file=sys.stderr)
        return 1

    print(f"GECTI: {len(scenes)} build sahnesi ve editör yapılandırması doğrulandı.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
