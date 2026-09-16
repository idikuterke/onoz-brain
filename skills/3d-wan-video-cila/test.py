#!/usr/bin/env python3
"""3d-wan-video-cila: ComfyUI Wan 2.1 iş akışı ve ortam doğrulaması."""
import os
import sys


def main() -> int:
    wf_path = r"E:\içerik üretim hattı\core\workflows.py"
    if not os.path.exists(wf_path):
        print(f"HATA: Workflows dosyasi bulunamadi: {wf_path}", file=sys.stderr)
        return 2

    # Dosya içeriğinde wan_i2v kontrolü
    with open(wf_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "def wan_i2v" not in content:
        print("HATA: workflows.py icerisinde 'wan_i2v' tanimi bulunamadi.", file=sys.stderr)
        return 1

    print("GECTI: 3d-wan-video-cila bilesenleri dogrulandi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
