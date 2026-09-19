# 3d-wan-video-cila — Wan 2.1 I2V ile sinematik video cilası

> Beceri kimliği: `3d-wan-video-cila` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Blender/Godot/Unity'den alınan ham viewport MP4'ünü ComfyUI Wan 2.1
Image-to-Video / Video-to-Video hattından geçirip gerçekçi ışık, sis, kumaş ve
deri dokusu eklemek için. Denoise 0.40–0.55 aralığında anatomi korunur, dokular
zenginleşir. Yalnızca **hareketin doğruluğunun önemsiz olduğu** kısa atmosfer
çekimlerinde: ortam tanıtımı, statik poz, kamera kaydırması.

## Kullanılmaz

- **Riglenmiş karakter animasyonu için.** Projenin kendi ölçümü (`docs/DEVAM.md`
  K9, 17 Eylül 2026): `wan_i2v` rig animasyonunu **atar ve hareketi uydurur**.
  Bu yüzden `donergec-3d` hattında `cila` adımı **kapalıdır**. 3D kukla
  hareketini "kılavuz aldığı" iddiası ölçümle çürütülmüştür; bu beceri hareket
  aktarmaz, görüntü üretir.
- Anatomik tutarlılığın kritik olduğu yerlerde (dövüş, el hareketi, diyalog jesti).
- Denoise 0.55 üstünde — anatomi bozulur; 0.40 altında — cila görünmez.
- Çıktının kanonik olması gereken yerde: bu adım deterministik değildir, aynı
  girdi iki koşuda aynı sonucu vermez.

## Nasıl çalışır

1. `core/workflows.py` içindeki `wan_i2v` iş akışı ComfyUI'ye gönderilir.
2. Girdi: ham viewport MP4. Çıktı: işlenmiş MP4.
3. Çağrı: `python "<hat>/mitoloji-3d/scripts/run.py" cila --only <karakter_id>`

## Doğrulama

```
python test.py
```

Beklenen: çıkış kodu 0. **Test ne ölçüyor, dürüstçe:** `core/workflows.py`
içinde `def wan_i2v` tanımının varlığını. Video kalitesini, hareket
sadakatini veya ComfyUI'nin ayakta olduğunu ÖLÇMEZ. Gerçek doğrulama
insan gözüyle yapılır; bu test yalnız "iş akışı silinmemiş" der.

## Sessiz hata riski

**Yüksek.** Çıktı "güzel" görünür ama hareket uydurulmuştur — K9 tam olarak
bunu yakaladı. Test geçer, video etkileyicidir, rig animasyonu kaybolmuştur.
Bu beceri tek başına hiçbir zaman L1'e çıkmamalı; yanına kare-kare poz
karşılaştırması gibi bir hareket sadakati ölçümü gerekir.
