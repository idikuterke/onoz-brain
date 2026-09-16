# 3d-mesh-temizle — Blender Headless Mesh Onarım ve Decimation

Yapay zeka (Trellis / Hunyuan) tarafından üretilen ham `.glb` mesh dosyalarındaki yozlaşmış yüzeyleri, kopuk parçaları (floating islands) temizler, çakışan vertex'leri birleştirir ve yüzey sayısını hedef limite indirger.

## Ne İşe Yarar?
- **Floating Island Temizliği:** Model dışındaki kopuk noktaları ayıklar.
- **Merge by Distance:** 0.0005 mesafe içindeki çift noktaları birleştirir.
- **Dissolve Degenerate:** Sıfır alanlı üçgenleri ve yozlaşmış kenarları siler.
- **Manifold Garantisi:** Non-manifold edge sayısını sıfıra indirir.
- **Decimate:** Modeli UV koordinatlarını koruyarak 45.000 yüzeye düşürür.

## Kullanım
```powershell
"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --background --python "E:\içerik üretim hattı\mitoloji-3d\blender_scripts\cleanup_mesh.py" -- <input_glb> <output_glb> [target_faces]
```

## Girdi ve Çıktı
- **Girdi:** Ham `.glb` dosyası.
- **Çıktı:** Temizlenmiş, UV dokulu ve optimize `.glb` dosyası.
- **Çıktı Logu:** `CLEANUP_RESULT:{"success": true, "final_faces": 45000, "is_manifold": true}`
