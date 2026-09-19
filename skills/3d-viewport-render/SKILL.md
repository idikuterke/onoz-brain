# 3d-viewport-render — headless Blender sahneleme ve kamera renderı

> Beceri kimliği: `3d-viewport-render` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Animasyonlu `.glb` karakteri stüdyo zeminine yerleştirip üç noktalı bozkır
ışığı (key + rim + ambient) ve sinematik kamera ile Eevee'de hızlı MP4 render
almak için. İki amaç: (1) hareketi göz kontrolü için hızlı önizleme, (2) Wan
cilası için anatomik olarak tutarlı girdi üretmek.

## Kullanılmaz

- **Karanlık sahnelerde bayt boyutuyla "boş kare" kararı vermek için.** K16:
  kurgan render'ı 43 KB'a sıkışınca kare boş sanıldı, doluydu. Karanlık sahne
  kapısı `ortalama_parlaklik` / `tepe_parlaklik` ölçümüyle çalışır, dosya
  boyutuyla değil.
- Final kalite render için — Eevee önizleme motorudur; Cycles ayrı iş.
- Kurgan gibi parametrik mekân sahneleri için — K11: mekân `core_3d/blender`
  ile parametrik kurulur, bu beceri karakter stüdyosu içindir.
- Blender 5.x ile (K10).

## Nasıl çalışır

1. Blender headless `blender_scripts/stage_and_render.py` koşar.
2. Zemin + üç ışık + kamera yolu kurulur, animasyon Eevee ile MP4'e basılır.
3. Girdi: animasyonlu `.glb`. Çıktı: viewport MP4.

## Doğrulama

```
python test.py
```

Beklenen: çıkış kodu 0. **Test ne ölçüyor, dürüstçe:** yalnızca
`stage_and_render.py` dosyasının **var olduğunu**. Render'ın çalıştığını, MP4
üretildiğini ya da karenin dolu olduğunu ÖLÇMEZ. Mevcudiyet kontrolüdür.

## Sessiz hata riski

**Yüksek.** İki bilinen sessiz hata modu: (1) karanlık kare — dosya küçük
olur, render "başarılı"dır, kare boştur (K16 bunu yakaladı); (2) ışık/kamera
kurulumu bozulur, video üretilir ama karakter kadraj dışındadır. Gerçek
doğrulama için çıktı MP4'ten bir kare alınıp parlaklık + kadraj kontrolü
gerekir — K16'daki parlaklık ölçümü zaten var, bu teste bağlanmalı.
