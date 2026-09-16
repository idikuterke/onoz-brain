#!/usr/bin/env python3
"""3d-viewport-render: stage_and_render.py dogrulama testi."""
import os
import sys


def main() -> int:
    script = r"E:\içerik üretim hattı\mitoloji-3d\blender_scripts\stage_and_render.py"
    if not os.path.exists(script):
        print(f"HATA: stage_and_render scripti bulunamadi: {script}", file=sys.stderr)
        return 2
    print("GECTI: 3d-viewport-render scripti mevcut.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
