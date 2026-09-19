#!/usr/bin/env python3
"""kos - bir beceriyi projede KOSTURUR ve sonucu sicile YAZAR. Tek komut.

    kos <beceri>                 # projenin icinde; .brain.json'dan projeyi bulur
    kos <beceri> --review-min 6  # soru sormadan
    kos <beceri> --dry-run       # kosturur ama sicile yazmaz

Neden var: brain log dogru seyi istiyor ama yanlis anda istiyor (dort alan,
elle). Bu sarmalayici verify komutunu GERCEKTEN kosturur, sonucu cikis
kodundan alir, tek soru sorar (inceleme dakikasi + mudahale) ve brain log'u
senin yerine cagirir. Sahte sicil yok: kosu gercek, sonuc gercek.

brain.py'ye dokunmaz (Ozellik Dondurma). anonim-export gibi bagimsiz betik.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path


def brain_home() -> Path:
    return Path(os.environ.get("BRAIN_HOME") or (Path.home() / "onoz-brain"))


def find_project(start: Path) -> tuple[str, Path]:
    """cwd'den yukari .brain.json arar; (proje_adi, proje_koku) dondurur."""
    for d in [start, *start.parents]:
        marker = d / ".brain.json"
        if marker.exists():
            data = json.loads(marker.read_text(encoding="utf-8"))
            return data["project"], d
    raise SystemExit(
        "HATA: .brain.json bulunamadi. Bir projenin icinde misin?\n"
        "      Baglamak icin: brain link <ad> <yol> --type <tip>"
    )


def load_skill(home: Path, skill_id: str) -> dict:
    p = home / "skills" / skill_id / "skill.json"
    if not p.exists():
        mevcut = sorted(x.name for x in (home / "skills").iterdir()
                        if (x / "skill.json").exists())
        raise SystemExit(f"HATA: beceri yok: {skill_id}\n      mevcut: {', '.join(mevcut)}")
    return json.loads(p.read_text(encoding="utf-8"))


def resolve_verify(verify: str, skill_dir: Path) -> str:
    """`python test.py ...` beceri dizinindeki test.py'yi kasteder; yolu ac.
    Diger komutlar (flutter test, npm run build...) proje kokunde oldugu gibi kosar."""
    m = re.match(r"^(python3?|py)\s+test\.py(\s.*)?$", verify.strip())
    if m:
        return f'{m.group(1)} "{skill_dir / "test.py"}"{m.group(2) or ""}'
    return verify


# YALNIZ kabugun "komut yok" mesajlari. Programin kendi ciktisi ("File not
# found" gibi) buraya GIRMEZ -- ilk gercek kosuda Godot'un "File not found"
# hatasi gercek bir KALDI'yi KOSAMADI saydirdi (2026-09-20). Genel "not found"
# deseni bu yuzden kaldirildi.
KOSAMADI_IZLERI = (
    "is not recognized as an internal or external command",   # cmd.exe
    ": command not found",                                    # bash/sh
    "komut bulunamadi",
)


def run_verify(cmd: str, cwd: Path) -> tuple[int, float, str]:
    t0 = time.monotonic()
    proc = subprocess.run(cmd, shell=True, cwd=str(cwd),
                          capture_output=True, text=True, errors="replace")
    dt = time.monotonic() - t0
    tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-8:])
    return proc.returncode, dt, tail


def kosamadi(rc: int, tail: str) -> bool:
    """Kapi KALDI mi, yoksa hic KOSAMADI mi? Ikincisi sicile yazilmaz."""
    if rc in (127, 9009):
        return True
    return rc != 0 and any(iz.lower() in tail.lower() for iz in KOSAMADI_IZLERI)


def ask_int(prompt: str) -> float:
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            v = float(raw)
            if v >= 0:
                return v
        except ValueError:
            pass
        print("  sayi gir (or. 4 veya 2.5)")


def ask_yes(prompt: str) -> bool:
    return input(prompt).strip().lower() in ("e", "evet", "y", "yes")


def main() -> int:
    ap = argparse.ArgumentParser(prog="kos", description=__doc__.split("\n")[0])
    ap.add_argument("skill", help="beceri kimligi (brain list)")
    ap.add_argument("--review-min", type=float, help="inceleme dakikasi (sorulmaz)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--autonomous", action="store_true", help="mudahale etmedim")
    g.add_argument("--assisted", action="store_true", help="mudahale ettim")
    ap.add_argument("--note", default="", help="sicil notu")
    ap.add_argument("--dry-run", action="store_true", help="kostur ama sicile yazma")
    args = ap.parse_args()

    home = brain_home()
    brain_py = home / "brain.py"
    if not brain_py.exists():
        raise SystemExit(f"HATA: brain.py yok: {brain_py}  (BRAIN_HOME dogru mu?)")

    project, root = find_project(Path.cwd())
    skill = load_skill(home, args.skill)
    verify = resolve_verify(skill["verify"], home / "skills" / args.skill)

    print(f"proje  : {project}  ({root})")
    print(f"beceri : {args.skill}  [{skill.get('level', 'L0')}]")
    print(f"kosuyor: {verify}\n")

    rc, dt, tail = run_verify(verify, root)
    if tail:
        print("  | " + tail.replace("\n", "\n  | "))

    if kosamadi(rc, tail):
        print(f"\nKOSAMADI (exit={rc}) - komut/arac bulunamadi. Sicile YAZILMADI.")
        print("Bu bir kapi sonucu degil, ortam sorunu. Araci PATH'e al ya da verify'i duzelt.")
        return 2

    result = "pass" if rc == 0 else "fail"
    print(f"\n{'GECTI' if rc == 0 else 'KALDI'}  (exit={rc}, {dt:.0f} sn)")

    if args.dry_run:
        print("--dry-run: sicile yazilmadi.")
        return 0 if rc == 0 else 1

    review = args.review_min if args.review_min is not None else ask_int(
        "inceleme kac dakika surdu? (ciktiyi okuma, diff'e bakma, karar) : ")
    if args.autonomous:
        auto = True
    elif args.assisted:
        auto = False
    else:
        auto = not ask_yes("mudahale ettin mi? (kod/test elle duzeltildi mi) [e/h] : ")

    cmd = [sys.executable, str(brain_py), "log", "--project", project,
           "--skill", args.skill, "--result", result, "--review-min", str(review)]
    if auto:
        cmd.append("--autonomous")
    note = args.note or f"kos: {verify[:60]} -> exit {rc}, {dt:.0f} sn"
    cmd += ["--note", note]
    out = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    print(out.stdout.strip() or out.stderr.strip())
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
