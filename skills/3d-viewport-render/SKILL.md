# 3d-viewport-render — Headless Blender Sahneleme ve Kamera Renderı

Animasyonlu `.glb` modelleri stüdyo zeminine yerleştirir, üç noktalı bozkır/fantastik ışıklandırması (key + rim + ambient) kurar ve sinematik kamera yörüngesi çizerek 30 FPS MP4 video çıktısı alır.

## Ne İşe Yarar?
- Karakterin animasyonunu hareketli kamera açısıyla kaydeder.
- AI Video-to-Video (Wan 2.1) aşamasına tutarlı anatomik girdi sağlar.
- Eevee motoru ile hızlı (saniyeler içinde) MP4 video renderı üretir.

## Kullanım
```powershell
"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --background --python "E:\içerik üretim hattı\mitoloji-3d\blender_scripts\stage_and_render.py" -- <animated_glb> <output_mp4> [frames] [fps]
```

## Girdi ve Çıktı
- **Girdi:** Animasyonlu `.glb`.
- **Çıktı:** 1280x720 H.264 MP4 videosu.
- **Çıktı Logu:** `RENDER_RESULT:{"success": true, "video_path": "...", "frames": 90}`
