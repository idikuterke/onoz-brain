# 3d-animasyon-paketle — Çoklu NLA Animasyon Track Paketleme

Rigged (kemikli) 3D karakter modellerine (Alp, Şaman, Tanrıça vb.) standart hareket kütüphanesini (idle, yürüme, saldırı, darbe alma, zafer nidası, konuşma) ayrı NLA (Non-Linear Animation) track'leri olarak tek bir `.glb` konteynerinde birleştirir.

## Ne İşe Yarar?
- Karakterin tek bir `.glb` dosyası içinde birden çok bağımsız animasyonu taşımasını sağlar.
- Godot 4 `AnimationPlayer` ve Unity `Animator` bileşenleri bu track'leri otomatik olarak algılar.
- Standart 6 hareket seti: `idle_combat`, `walk_forward`, `sword_slash`, `take_damage`, `victory_shout`, `talk_gesture`.

## Kullanım
```powershell
"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --background --python "E:\içerik üretim hattı\mitoloji-3d\blender_scripts\pack_animations.py" -- <base_rigged_glb> <output_glb> [actions_json]
```

## Girdi ve Çıktı
- **Girdi:** Kemikli baz model (`.glb`).
- **Çıktı:** NLA track'leri gömülü `.glb` animasyon paketi.
- **Çıktı Logu:** `PACK_RESULT:{"success": true, "packed_actions": ["idle_combat", "walk_forward", ...]}`
