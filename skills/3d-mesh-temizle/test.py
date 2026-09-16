#!/usr/bin/env python3
"""3d-mesh-temizle: Blender headless ve cleanup_mesh.py dogrulama testi."""
import os
import subprocess
import sys


def main() -> int:
    blender_exe = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
    script_path = r"E:\içerik üretim hattı\mitoloji-3d\blender_scripts\cleanup_mesh.py"

    if not os.path.exists(blender_exe):
        print(f"HATA: Blender bulunamadi: {blender_exe}", file=sys.stderr)
        return 2

    if not os.path.exists(script_path):
        print(f"HATA: Script bulunamadi: {script_path}", file=sys.stderr)
        return 2

    cmd = [blender_exe, "--background", "--python-expr", "import bpy; print('BLENDER_OK')"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0 or "BLENDER_OK" not in proc.stdout:
        print("HATA: Blender headless test basarisiz oldu.", file=sys.stderr)
        return 1

    print("GECTI: 3d-mesh-temizle araclari ve Blender hazir.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
