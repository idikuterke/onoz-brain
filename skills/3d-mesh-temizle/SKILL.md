# 3d-mesh-temizle — Blender headless mesh onarımı ve decimation

> Beceri kimliği: `3d-mesh-temizle` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Trellis / Hunyuan gibi görüntüden-3D üreticilerin verdiği ham `.glb`
mesh'lerini oyun motoruna sokmadan önce temizlemek için: kopuk parçalar
(floating islands), 0.0005 mesafe içindeki çift noktalar, sıfır alanlı üçgenler
ve yozlaşmış kenarlar. Her AI üretimi mesh'in **ilk** ve **zorunlu** adımı.

## Kullanılmaz

- **Riglenecek karakter gövdeleri için.** Projenin K1 kararı (`docs/DEVAM.md`):
  görüntüden-3D yanlış topoloji verir, temizlik bunu düzeltmez — riglenmiş temel
  gövde (MPFB2) kullanılır. Bu beceri prop ve dekor içindir, karakter için değil.
- Elle modellenmiş, topolojisi kasıtlı mesh'lerde — decimation kasıtlı kenar
  akışını bozar.
- Merge mesafesi 0.0005'in üstüne çıkarılarak — ince detaylar (parmak, kulak)
  birleşir.
- Blender 5.x ile — K10: MPFB2'de Blender 5 kırılması var, hat 4.5'te kalır.

## Nasıl çalışır

1. Blender 4.5 `--background` modunda `blender_scripts/cleanup_mesh.py` koşar.
2. Sırayla: floating island temizliği → merge by distance → dissolve degenerate
   → decimation.
3. Girdi: ham `.glb`. Çıktı: temizlenmiş `.glb`.

## Doğrulama

```
python test.py
```

Beklenen: çıkış kodu 0. **Test ne ölçüyor:** Blender 4.5'in kurulu olduğunu ve
`--background --python-expr` ile gerçekten başlayıp `BLENDER_OK` bastığını,
ayrıca `cleanup_mesh.py`'nin var olduğunu. Dört beceri içinde gerçek bir
çalışma zamanı denetimi yapan **tek** test bu. Ama temizliğin doğru olduğunu
(poly sayısı, kopuk parça sayısı) ÖLÇMEZ.

## Sessiz hata riski

Var. Temizlik "başarılı" döner ama agresif decimation siluet detayını yemiş
olabilir; ya da floating island sayılan parça aslında kasıtlı bir aksesuardır.
Çıktı poly sayısı ve bağlı bileşen sayısı loglanmalı, eşik dışı sapmada
kalmalı — şu an loglanmıyor.
