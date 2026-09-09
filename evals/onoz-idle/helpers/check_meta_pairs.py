#!/usr/bin/env python3
"""Unity Assets dizinindeki her dosya/klasor ile .meta dosyasinin birebir eslesmesini denetler."""
from pathlib import Path
import sys

def main() -> int:
    root = Path("Assets")
    if not root.exists():
        print("HATA: Assets dizini bulunamadi.", file=sys.stderr)
        return 1

    missing_meta = []
    orphan_meta = []

    for p in root.rglob("*"):
        if p.name.endswith(".meta"):
            target = p.with_name(p.name[:-5])
            if not target.exists():
                orphan_meta.append(str(p))
        else:
            meta = p.with_name(p.name + ".meta")
            if not meta.exists():
                missing_meta.append(str(p))

    if missing_meta or orphan_meta:
        if missing_meta:
            print(f"KALDI: {len(missing_meta)} asset icin .meta dosyasi eksik:", file=sys.stderr)
            for m in missing_meta[:5]:
                print(f"  - {m}", file=sys.stderr)
        if orphan_meta:
            print(f"KALDI: {len(orphan_meta)} sahipsiz .meta dosyasi var:", file=sys.stderr)
            for o in orphan_meta[:5]:
                print(f"  - {o}", file=sys.stderr)
        return 1

    print("GECTI: Tum asset ve .meta dosyalari birebir eslesiyor.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
