# KALDI kanıtları — Flutter hattı (2026-09-09)

> `AGENT_EVAL_SPEC` kırmızı çizgi 1: ölçtüğü şey yokken görev geçiyorsa, görev
> hiçbir şey ölçmüyordur. Aşağıdaki mutasyonlar bizzat koşuldu, `--record`
> verilmedi (sicil kirlenmedi) ve her koşudan sonra hedef ağaç bire bir geri geldi.

## gokyuzu-gunlugu — baseline 3/3

| Görev | Mutasyon | Sonuç |
|---|---|---|
| GG-01 `flutter analyze` | `lib/_denetim_mut.dart` içine tip hatası (`int x = "..."`) | **KALDI** 0/1 → dosya silindi → GEÇTİ |
| GG-02 `flutter test` | `test/_denetim_mut_test.dart`, `expect(1, 2)` | **KALDI** 0/1 → dosya silindi → GEÇTİ |
| GG-03 `--plain-name "key ve parseKey simetrik"` | eşleşmeyen ad ile koşuldu | **exit 79** ("No tests match") — test silinse/yeniden adlandırılsa görev kalır |

Ağaç: 8 kirli dosyayla başladı, 8 ile bitti.

## gokyazi — baseline 1/2

| Görev | Mutasyon | Sonuç |
|---|---|---|
| YZ-01 `flutter analyze` | gerek yok — **bugün zaten KALIYOR** (22 issue, exit 1) | ayırt ettiği kanıtlı |
| YZ-02 `flutter test` | `test/_denetim_mut_test.dart`, `expect(1, 2)` | **KALDI** 0/1 → silindi → GEÇTİ |

Ağaç: 3 → 3.

## rota — baseline 1/2

| Görev | Mutasyon | Sonuç |
|---|---|---|
| RT-01 `flutter analyze` | `lib/_denetim_mut.dart` tip hatası | **KALDI** 0/1 → silindi → GEÇTİ |
| RT-02 `flutter test` | gerek yok — **bugün zaten KALIYOR** (`RotaApp builds` başarısız, exit 1) | ayırt ettiği kanıtlı |

Ağaç: 68 → 68 (proje 4 aydır uykuda, kirlilik önceden vardı; mutasyon kalıntı bırakmadı).

## Yol boyunca çıkan iki tuzak

**1. Boru hattı çıkış kodu.** `flutter test ... | tail -3; echo $?` **tail'in** kodunu
verir, flutter'ınkini değil. İlk ölçümde `--plain-name` eşleşmeyince "exit 0" göründü
ve görev ayırt etmiyor sanıldı; borusuz ölçümde gerçek kod **79** çıktı. Eval görevi
yazarken çıkış kodu daima borusuz doğrulanmalı.

**2. `git commit` index'i commit eder, `git add` ettiğini değil.** `git add STATUS.md`
sonrası düz `git commit`, `tengri_fast_app`'te kullanıcının önceden stage'lenmiş 6
dosyasını da içine aldı. `git reset --soft HEAD~1` ile geri alındı (stage durumu
korunur) ve `git commit -- STATUS.md` pathspec biçimiyle yalnız o dosya commit'lendi.
Hedef projede commit atarken **daima pathspec kullan**.

---

# RT-A01 (ajan görevi) — tasarım doğrulaması, 2026-09-09

| Kontrol | Sonuç |
|---|---|
| `setup` sonrası verify KALIYOR mu (k.ç. 1) | ✅ `VERIFY_EXIT=1` |
| "Testi sil" hilesi tutuyor mu | ❌ tutmuyor — `flutter test` **1**, `--plain-name` **1** (dosya hiç yokken "No tests were found") |
| `teardown` ağacı temiz bırakıyor mu | ✅ 0 kirli dosya, bekleyen deneme yok |

**Bilinen sınır:** verify, testin *silinmesini* ve *adının değişmesini* makineyle
engelliyor ama **içinin boşaltılmasını** (örn. `pumpWidget` kaldırılıp
`expect(true, true)` bırakılması) engelleyemiyor. Prompt bunu açıkça yasaklıyor;
denetim, çözücünün raporu okunarak yapılır. Verify'a dosya içeriği grep'i eklemek
düşünüldü ama çözümün şeklini gereksiz kısıtladığı için **eklenmedi** — KA-07'de
öğrenildiği gibi, doğrulama gerçek şeyi ölçmeli, geçerli çözümleri bloklayan bir
vekil değil.

---

# icerik-hatti (IH-01, IH-02) — 2026-09-09

| Görev | Mutasyon | Sonuç |
|---|---|---|
| IH-01 tüm .py derlenir | `core/_denetim_mut.py` bozuk sözdizimi | **KALDI** 0/1 → silindi → GEÇTİ |
| IH-02 config bütünlüğü | `gokyazi-tarot/configs/pipeline.json` bozuk JSON | **KALDI** 0/1 → geri → GEÇTİ |

Ağaç 11 kirli dosyayla başladı, 11 ile bitti.

**`python -m core saglik` bilerek eval görevi YAPILMADI.** Çalışan bir ComfyUI
sunucusuna bakıyor (`sunucu: ok (surum 0.35.0, RAM bos 10.0 GB)`); sunucu kapalıyken
kalır ve projeyi değil ortamı ölçer. Aynı gerekçe Ajan 2'nin Unity `-runTests`
kararında da geçerliydi. `saglik` elle koşulan bir kapı olarak kalır; eval seti
sunucudan bağımsız, deterministik ölçülerle sınırlı tutuldu.
