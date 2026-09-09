#!/usr/bin/env python3
"""IH-01: Tum Python kaynaklari (core/ + hat scriptleri) derlenir.

Cikis: 0 = hepsi derlendi, 1 = derleme hatasi, 2 = hic dosya bulunamadi.
Not: ComfyUI sunucusuna DOKUNMAZ; deterministiktir.
"""
import pathlib
import py_compile
import sys

KOKLER = ["core"]
HAT_DESENI = "*/scripts"
ATLA = {"__pycache__", ".git", ".cache", "outputs", "node_modules"}


def dosyalar():
    kok = pathlib.Path(".")
    for k in KOKLER:
        for p in pathlib.Path(k).rglob("*.py"):
            if not (set(p.parts) & ATLA):
                yield p
    for p in kok.glob(HAT_DESENI):
        for f in p.rglob("*.py"):
            if not (set(f.parts) & ATLA):
                yield f


def main() -> int:
    toplam = 0
    hatalar = []
    for f in dosyalar():
        toplam += 1
        try:
            py_compile.compile(str(f), doraise=True, cfile=None)
        except py_compile.PyCompileError as exc:
            hatalar.append(f"{f}: {exc.msg.splitlines()[0] if exc.msg else exc}")
            print(f"DERLEME_HATASI {f}", file=sys.stderr)
    print(f"KAYNAK_TOPLAM={toplam}")
    print(f"KAYNAK_HATA={len(hatalar)}")
    if toplam == 0:
        print("HATA: hic .py bulunamadi, tarama yolu bozuk olabilir.", file=sys.stderr)
        return 2
    if hatalar:
        for h in hatalar[:5]:
            print("  - " + h, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
