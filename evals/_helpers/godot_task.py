#!/usr/bin/env python3
"""Eval verify komutlari icin Windows/cmd.exe uyumlu Godot kosucu.

brain.py cmd_eval, verify komutunu `subprocess.run(shell=True)` ile cmd.exe
altinda kosturur; bash sozdizimi (command -v, grep, $VAR) burada calismaz.
Bu yardimci tum Godot tabanli verify komutlarinin ortak ucu olarak yazildi.

Cikis kodlari (eval gorevlerinin anlam sozlesmesi):
  0 = temiz
  1 = hata (marker eslesmesi / godot sifirdan farkli cikis / artifact yok /
      --require-line beklenen ciktiyi uretmedi)
  2 = ortam hatasi (godot veya yardimci script bulunamadi, gecersiz marker)
  3 = zaman asimi

--require-line: sessiz-hata kapani. "godot 0 dondu" tek basina yetmez;
beklenen basari ciktisi (orn. "PASS test_envanter.gd/") gercekten uretildiyse
gecti denir. Modul listeden cikarilirsa gorev YANLIS gecmez, KALDI.

Stdout bilerek yalnizca ASCII'dir: brain.py capture_output'u text=True ve
strict decoder ile yapar; Godot'un UTF-8 ciktisi dogrudan ulasirsa
UnicodeDecodeError ile tum eval cokebilir. Bu yardimci o riski izole eder.
"""
import argparse
import os
import re
import shlex
import subprocess
import sys

DEFAULT_GODOT = r"C:\Godot\Godot_v4.7.1-stable_win64_console.exe"


def _ascii(text: str) -> str:
    """brain.py'nin strict decoder'ina guvenli ASCII dondurur."""
    return text.encode("ascii", "replace").decode("ascii")


def _compile_patterns(patterns, what: str) -> list:
    out = []
    for rx in patterns:
        try:
            out.append((rx, re.compile(rx)))
        except re.error as exc:
            print(f"HATA: gecersiz {what} regex: {rx!r} ({exc})")
            raise SystemExit(2)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Godot eval gorevi kosucu")
    ap.add_argument("--mode", choices=["run", "scan"], required=True,
                    help="run: godot cikis kodu belirleyici; scan: marker regex belirleyici")
    ap.add_argument("--marker", action="append", default=[],
                    help="scan modunda hata sayilan regex (tekrarlanabilir, OR)")
    ap.add_argument("--require-line", action="append", default=[],
                    help="ciktida EN AZ BIR kez eslesmesi beklenen regex (tekrarlanabilir); "
                         "eslesmezse sonuc 1. Sessiz-hata kapani.")
    ap.add_argument("--base-args", default="",
                    help='godot argumanlari tek string, ornek: "--headless --path ."')
    ap.add_argument("--arg", action="append", default=[],
                    help="ek godot argumani, tek token (bosluklu degerler icin)")
    ap.add_argument("--gd", default=None,
                    help="-s ile kosulacak SceneTree yardimci scripti (mutlak yol)")
    ap.add_argument("--user-arg", action="append", default=[],
                    help="script'e -- sonrasi gecen kullanici argumani")
    ap.add_argument("--expect-artifact", default=None,
                    help="run sonrasi var olmasi beklenen dosya (yoksa 1)")
    ap.add_argument("--godot", default=DEFAULT_GODOT)
    ap.add_argument("--timeout", type=int, default=0,
                    help="saniye; 0 = sinirsiz (dis timeout'a brain.py bakar)")
    args = ap.parse_args()

    try:
        markers = _compile_patterns(args.marker, "marker")
        requires = _compile_patterns(args.require_line, "require-line")
    except SystemExit:
        return 2

    if not os.path.isfile(args.godot):
        print(f"HATA: godot bulunamadi: {args.godot}")
        return 2

    # shlex posix=False: Windows yollarindaki ters bolu korunur; cift tirnak
    # token'da kalir, asagida elle soyulur.
    godot_args = shlex.split(args.base_args, posix=False)
    godot_args = [t[1:-1] if len(t) >= 2 and t[0] == t[-1] == '"' else t
                  for t in godot_args]

    if args.gd:
        if not os.path.isfile(args.gd):
            print(f"HATA: yardimci script bulunamadi: {args.gd}")
            return 2
        godot_args += ["-s", args.gd]
    godot_args += args.arg
    if args.user_arg:
        godot_args += ["--"] + args.user_arg

    cmd = [args.godot] + godot_args
    try:
        proc = subprocess.run(cmd, capture_output=True,
                              timeout=(args.timeout or None))
    except subprocess.TimeoutExpired:
        print(f"HATA: {args.timeout}s icinde bitmedi")
        return 3

    output = ((proc.stdout or b"") + b"\n" + (proc.stderr or b"")) \
        .decode("utf-8", "replace")
    lines = output.splitlines()

    hits = []
    for _, cre in markers:
        hits += [ln for ln in lines if cre.search(ln)]

    print(f"GODOT_EXIT={proc.returncode}")
    shown = hits if hits else [ln for ln in lines
                               if re.search(r"FAIL|ERROR|TOPLAM|OZET|PARSE", ln)]
    for ln in shown[:30]:
        print("  " + _ascii(ln))

    if args.mode == "scan":
        # Orijinal sozlesme: hata markiri varsa 1, temizse 0.
        # (godot cikis kodu scan modunda belirleyici degildi, hala degil.)
        if hits:
            print(f"KALDI: {len(hits)} marker eslesmesi")
            return 1
        missing = [rx for rx, cre in requires
                   if not any(cre.search(ln) for ln in lines)]
        if missing:
            print(f"KALDI: beklenen cikti uretilmedi: {missing}")
            return 1
        print("GECTI: hata markiri yok")
        return 0

    # run modu: cikis kodu (ve varsa artifact + require-line) belirleyici.
    if proc.returncode != 0:
        print(f"KALDI: godot cikis kodu {proc.returncode}")
        return 1
    if args.expect_artifact and not os.path.isfile(args.expect_artifact):
        print(f"KALDI: beklenen artifact yok: {args.expect_artifact}")
        return 1
    missing = [rx for rx, cre in requires
               if not any(cre.search(ln) for ln in lines)]
    if missing:
        print(f"KALDI: beklenen cikti uretilmedi: {missing}")
        return 1
    print("GECTI")
    return 0


if __name__ == "__main__":
    sys.exit(main())