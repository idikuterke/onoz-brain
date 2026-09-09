#!/usr/bin/env python3
"""IH-02: Yapilandirma butunlugu.

- configs/global.json gecerli JSON ve zorunlu anahtarlari tasiyor
- her hattin configs/pipeline.json'i gecerli JSON
Cikis: 0 = tamam, 1 = bozuk/eksik, 2 = hic pipeline.json bulunamadi.
Deterministiktir; ComfyUI sunucusuna dokunmaz.
"""
import json
import pathlib
import sys

ZORUNLU = ["version", "python", "comfyui", "paths", "fonts", "models"]


def main() -> int:
    hatalar = []

    g = pathlib.Path("configs/global.json")
    if not g.exists():
        print("KALDI: configs/global.json yok", file=sys.stderr)
        return 1
    try:
        veri = json.loads(g.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"KALDI: configs/global.json bozuk JSON: {exc}", file=sys.stderr)
        return 1
    eksik = [k for k in ZORUNLU if k not in veri]
    if eksik:
        hatalar.append(f"configs/global.json eksik anahtar: {eksik}")

    pipelines = sorted(pathlib.Path(".").glob("*/configs/pipeline.json"))
    for p in pipelines:
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            hatalar.append(f"{p}: bozuk JSON ({exc})")

    print(f"PIPELINE_SAYISI={len(pipelines)}")
    print(f"CONFIG_HATA={len(hatalar)}")
    if not pipelines:
        print("HATA: hic pipeline.json bulunamadi.", file=sys.stderr)
        return 2
    if hatalar:
        for h in hatalar:
            print("  - " + h, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
