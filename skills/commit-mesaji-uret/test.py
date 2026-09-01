#!/usr/bin/env python3
"""commit-mesaji-uret: mesaji conventional commit biçimine sokar.

Kural: `tip(scope)?(!)?: açıklama`  (tip: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)

Cikis kodlari:
  0 = mesaj gecerli (veya --selftest'te tum ornekler beklendigi gibi)
  1 = mesaj gecersiz (veya selftest'te bir ornek sasti)
  2 = on kosul eksik: mesaj verilmedi / dosya okunamadi
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CONVENTIONAL_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\(([a-z0-9._/-]+)\))?!?: (\S.*)$"
)

SELFTEST = [
    ("feat: toplama ekrani eklendi", True),
    ("fix(engine): null referans duzeltildi", True),
    ("feat(api)!: geriye donuk olmayan degisiklik", True),
    ("chore: bagimlilik guncellemesi", True),
    ("revert: onceki commit geri alindi", True),
    ("Feature: buyuk harfli tip", False),
    ("feat:bosluk-yok", False),
    ("feat: ", False),
    ("hata duzeltildi", False),
    ("feat(cok genis scope): x", False),
    ("fix", False),
]


def validate(message: str) -> bool:
    return bool(CONVENTIONAL_RE.match(message))


def main() -> int:
    ap = argparse.ArgumentParser(description="conventional commit mesajini dogrular")
    ap.add_argument("--message", help="dogrulancak mesaj (tek satir)")
    ap.add_argument("--message-file", help="mesajin okunacagi dosya (ilk satir)")
    ap.add_argument("--selftest", action="store_true",
                    help="dahili orneklerle regex'i dogrula (0/1)")
    ap.add_argument("--project", help="(kabul edilir ama dogrulamaya etkisi yok)")
    args = ap.parse_args()

    if args.selftest:
        failed = [(msg, ok) for msg, ok in SELFTEST if validate(msg) != ok]
        for msg, ok in failed:
            print(f"SAPTI: {msg!r} -> beklenen {'gecerli' if ok else 'gecersiz'}",
                  file=sys.stderr)
        print(f"SELFTEST: {len(SELFTEST) - len(failed)}/{len(SELFTEST)} gecti")
        return 0 if not failed else 1

    if args.message_file:
        try:
            message = Path(args.message_file).read_text(encoding="utf-8").rstrip("\n")
        except OSError as exc:
            print(f"HATA: mesaj dosyasi okunamadi: {exc}", file=sys.stderr)
            return 2
    elif args.message:
        message = args.message
    else:
        print("HATA: --message, --message-file veya --selftest gerekiyor", file=sys.stderr)
        return 2

    if validate(message):
        print(f"GECERLI: {message}")
        return 0
    print(f"GECERSIZ: {message}", file=sys.stderr)
    print("Beklenen: tip(scope)!: aciklama  (tip kucuk harf: feat|fix|docs|style|"
          "refactor|perf|test|build|ci|chore|revert)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
