#!/usr/bin/env python3
"""3d-animasyon-paketle: pack_animations.py dogrulama testi."""
import os
import sys


def main() -> int:
    script = r"E:\içerik üretim hattı\mitoloji-3d\blender_scripts\pack_animations.py"
    if not os.path.exists(script):
        print(f"HATA: pack_animations scripti bulunamadi: {script}", file=sys.stderr)
        return 2
    print("GECTI: 3d-animasyon-paketle scripti mevcut.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
