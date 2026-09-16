# 3d-wan-video-cila — Wan 2.1 I2V ile Sinematik Video İyileştirme

3D motorlarından (Blender/Godot/Unity) alınan ham animasyon videolarını ComfyUI Wan 2.1 Image-to-Video / Video-to-Video boru hattına sokarak gerçekçi ışık, sis, doku ve mitolojik atmosferle sinematik bir filme dönüştürür.

## Ne İşe Yarar?
- Ham 3D "oyun görüntüsü" hissini ortadan kaldırır; gerçekçi kumaş, deri ve saç detayları ekler.
- 3D kukla hareketini kılavuz alarak AI video modellerindeki rastgele deformasyon ve tutarsızlık sorununu çözer.
- Denoise oranı: 0.40 – 0.55 (Anatomi bozulmaz, dokular zenginleşir).

## Kullanım
```powershell
C:\Python313\python.exe "E:\içerik üretim hattı\mitoloji-3d\scripts\run.py" cila --only <karakter_id>
```

## Girdi ve Çıktı
- **Girdi:** Ham viewport MP4 videosu.
- **Çıktı:** 8K/HD Sinematik kalitede işlenmiş video.
