# Ajan eval görevleri — tasarım sözleşmesi

## Neden ayrı bir tür

`kind: "regression"` görevleri **proje sağlığını** ölçer: derleniyor mu, sahne açılıyor mu.
Ajan hiçbir şey yapmasa da geçerler. Oranı ~%100 olmalı; düşerse proje bozulmuştur.

`kind: "agent"` görevleri **ajan otonomisini** ölçer: bozuk bir durum kurulur, ajandan
düzeltmesi istenir, komut doğrular. Baseline sıfıra yakın olmalı — yükseltilecek sayı budur.

İkisini tek orana karıştırırsan hiçbirini ölçmüş olmazsın. `brain eval` artık ikisini
ayrı raporluyor.

## Görev formatı

```json
{
  "id": "KA-A01",
  "kind": "agent",
  "title": "Kirik NPC etkilesim sinyalini onar",
  "setup": "git stash list >/dev/null; python $BRAIN_HOME/evals/_helpers/break.py --case npc-signal",
  "prompt": "NPC'ye yaklasinca etkilesim ipucu cikmiyor. Sebebini bul ve duzelt.",
  "verify": "godot --headless --path . -s res://tests/test_npc_interact.gd",
  "teardown": "git checkout -- .",
  "timeout": 300,
  "needs_adjust": false
}
```

- `setup` — bozuk durumu **deterministik** kurar. Rastgele bozma yasak; her koşuda aynı durum.
- `prompt` — ajana verilecek metin. Çözümü içermez, sadece belirtiyi tarif eder.
- `verify` — tek komut, geçti/kaldı. `setup` çalıştıktan hemen sonra **kalmalı**.
- `teardown` — `finally` içinde her zaman çalışır. `git checkout -- .` en güvenlisi.

## Kırmızı çizgiler

1. **`setup` sonrası `verify` geçiyorsa görev bozuktur.** Yeni görev eklerken önce bunu
   test et: kur, doğrula, "KALDI" görmelisin. Görmüyorsan görev hiçbir şey ölçmüyor.
2. **`teardown` olmadan görev eklenmez.** Eval koşusu projeyi kirli bırakmamalı.
3. **Zaten geçen bir şeyi görev yapma.** Baseline'ı şişirir, headroom bırakmaz.
4. **Eval seti dondurulur.** Kalibrasyondan sonra görev metni değişirse geçmiş
   ölçümler karşılaştırılamaz. Yeni görev eklenir, eski değiştirilmez.

## İlk 6 ajan görevi — Kut'un Arınışı

Kolaydan zora. `setup` kancalarını `evals/_helpers/break.py` içinde topla.

| ID | Bozulan durum | Doğrulama |
|---|---|---|
| KA-A01 | Bir `.gd` dosyasında sinyal bağlantısı silinir | ilgili test geçer |
| KA-A02 | Envanter kapasite sınırı kaldırılır (off-by-one) | `test_inventory.gd` |
| KA-A03 | Görev zinciri 2. aşama koşulu ters çevrilir | `test_quest_chain.gd` |
| KA-A04 | Sahneden bir node yeniden adlandırılır, referans kırılır | sahne smoke test |
| KA-A05 | Yeni test yazdırılır: Yelbegen ölüm sinyali (KA-07'nin eksik testi) | test dosyası var + geçer |
| KA-A06 | Yeni test yazdırılır: save round-trip (KA-10'un eksiği) | test dosyası var + geçer |

KA-A05 ve KA-A06 iki iş birden yapar: hem ajan otonomisini ölçer, hem regresyon
setindeki iki boşluğu kapatır. Bunlarla başla.

## Koşum

```bash
brain eval kutun-arinisi --kind regression    # proje sagligi, ~%100 bekle
brain eval kutun-arinisi --kind agent         # otonomi, dusuk baslar
brain eval kutun-arinisi --record             # ikisi birden, kayit
```
