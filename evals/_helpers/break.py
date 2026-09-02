#!/usr/bin/env python3
"""Ajan eval gorevleri icin deterministik bozma kancalari.

Sozlesme: her --case, projede TEK ve TEKRARLANABILIR bir bozulma yapar.
Rastgelelik yasak. Geri alma teardown'un isidir; kancalar kendi kendine
geri alinmaz. Cikis: 0 = bozma uygulandi, 2 = hedef bulunamadi.

KALIBRASYON NOTLARI (2026-09-02, AutoCoder - Tunga gercek agaci):
- npc-signal: etkilesim zinciri (etkilesim_hedefi_degisti emit) MEVCUT test
  paketi tarafindan KAPSANMIYOR (test_etkilesim yalniz en_yakin/sahne yapisi/
  DataDB/ipucu_metni test eder). Kanit: 2026-09-02 suit kosumu - bozma
  uygulandi, test_etkilesim gecti. Bu kör nokta KA-A07 ile kapatilacak;
  KA-A01 ancak ondan sonra eklenebilir.
- inventory-stack: Tunga'da kapasite mekaniği YOK (GameState.esya_ekle
  limitsiz yiginlar). Kancasi testle KANITLANMIS bozmaya bagli: yigin
  uzer-yazmasi (test_envanter + test_boss yakalar, kanitli kosum).
- ka-a05-yelbegen-test-yok / ka-a07-zincir-testi-yok: kirli durum = ilgili
  test dosyasinin henuz yazilmamis olmasi. Setup ve teardown ayni kancadir:
  ajanin yazdigi dosyayi kaldirir (olcum taze baslar). Tunga agaci
  kirliyken `git checkout -- .` TEARDOWN KULLANILMAZ; stash sonrasi
  temiz agacta A07'nin teardown'u guvenli hale gelir.
"""
import argparse
import sys
from pathlib import Path

CASES = {}


def case(name):
    def deco(fn):
        CASES[name] = fn
        return fn
    return deco


def patch(path: Path, old: str, new: str) -> int:
    if not path.exists():
        print(f"HATA: dosya yok: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    if old not in text:
        print(f"HATA: hedef desen bulunamadi: {path} <- {old!r}", file=sys.stderr)
        return 2
    if text.count(old) > 1:
        print(f"HATA: desen {text.count(old)} kez geciyor, tekil olmali: {path}", file=sys.stderr)
        return 2
    path.write_text(text.replace(old, new), encoding="utf-8")
    print(f"BOZULDU: {path}")
    return 0


def remove_if_exists(path: Path) -> int:
    if path.exists():
        path.unlink()
        print(f"KALDIRILDI: {path}")
    else:
        print(f"ZATEN YOK: {path}")
    return 0


@case("npc-signal")
def npc_signal(_):
    return patch(Path("scripts/player/etkilesim_dedektoru.gd"),
                 "EventBus.etkilesim_hedefi_degisti.emit(_mevcut_hedef)",
                 "# BOZULDU: EventBus.etkilesim_hedefi_degisti.emit(_mevcut_hedef)")


@case("inventory-stack")
def inventory_stack(_):
    return patch(Path("scripts/core/game_state.gd"),
                 "envanter[id] = mevcut + adet",
                 "envanter[id] = adet  # BOZULDU: yigin uzer-yazmasi")


@case("ka-a05-yelbegen-test-yok")
def ka_a05_yelbegen_test_yok(_):
    return remove_if_exists(Path("tests/test_yelbegen.gd"))


@case("ka-a07-zincir-testi-yok")
def ka_a07_zincir_testi_yok(_):
    return remove_if_exists(Path("tests/test_etkilesim_zinciri.gd"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True, choices=sorted(CASES))
    args = ap.parse_args()
    return CASES[args.case](args)


if __name__ == "__main__":
    sys.exit(main())