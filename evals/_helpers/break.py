#!/usr/bin/env python3
"""Ajan eval gorevleri icin deterministik bozma kancalari.

Sozlesme: her --case, projede TEK ve TEKRARLANABILIR bir bozulma yapar.
Rastgelelik yasak. Geri alma teardown'un isidir; kancalar kendi kendine
geri alinmaz. Cikis: 0 = bozma uygulandi, 2 = hedef bulunamadi.

KALIBRASYON NOTLARI (2026-09-02, AutoCoder - Tunga gercek agaci):
- npc-signal: etkilesim zinciri (etkilesim_hedefi_degisti emit) MEVCUT test
  paketi tarafindan KAPSANMIYOR (test_etkilesim yalniz en_yakin/sahne yapisi/
  DataDB/ipucu_metni test eder). Kirmizi cizgi testi "verify KALDI" uretmez;
  KA-A01 eklenmeden once zinciri kapsayan bir test yazilmalidir.
- inventory-capacity: Tunga'da kapasite mekaniği YOK (GameState.esya_ekle
  limitsiz yiginlar). Kancasi bu yuzden testle KANITLANMIS bir bozmaya
  baglandi: yigin uzer-yazmasi (test_envanter yakalar, asagida kanitli).
- ka-a05-yelbegen-test-yok: kirli durum = KA-07'nin eksik testinin hala
  yazilmamis olmasi. Tekrarlanabilirlik icin setup her kosumda dosyayi
  siler (ajan onceki kosumda yazsa bile); teardown ayni kancadir.
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


# --- kalibre edilmis kancalar (Tunga gercek agaci) -----------------------

@case("npc-signal")
def npc_signal(_):
    # GERCEK zincir: etkilesim_dedektoru -> EventBus.etkilesim_hedefi_degisti
    # -> etkilesim_ipucu._hedef_degisti. Dikkat: test kapsami yok (ustteki nota bak).
    return patch(Path("scripts/player/etkilesim_dedektoru.gd"),
                 "EventBus.etkilesim_hedefi_degisti.emit(_mevcut_hedef)",
                 "# BOZULDU: EventBus.etkilesim_hedefi_degisti.emit(_mevcut_hedef)")


@case("inventory-stack")
def inventory_stack(_):
    # Kapasite mekaniği olmadigi icin testle yakalanan gercek bozma: yigin
    # uzer-yazmasi. test_envanter._test_esya_yiginlama yakalar (kanitlandi:
    # 2026-09-02 suit kosumu, FAIL test_envanter.gd).
    return patch(Path("scripts/core/game_state.gd"),
                 "envanter[id] = mevcut + adet",
                 "envanter[id] = adet  # BOZULDU: yigin uzer-yazmasi")


@case("ka-a05-yelbegen-test-yok")
def ka_a05_yelbegen_test_yok(_):
    # Kirli durum: Yelbegen olum sinyali testi yazilmamis. Setup ve teardown
    # ayni kancadir: ajanin yazdigi test dosyasini kaldirir (olcum taze
    # baslar). Tunga agaci kirli oldugu icin `git checkout -- .` TEARDOWN
    # OLARAK KULLANILMAZ - kullanici calismasini siler.
    return remove_if_exists(Path("tests/test_yelbegen.gd"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True, choices=sorted(CASES))
    args = ap.parse_args()
    return CASES[args.case](args)


if __name__ == "__main__":
    sys.exit(main())