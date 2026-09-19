# 3d-animasyon-paketle — çoklu NLA animasyon track paketleme

> Beceri kimliği: `3d-animasyon-paketle` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Riglenmiş bir karakterin (`Alp`, `Şaman`, `Tanrıça` …) standart hareket
kütüphanesini tek bir `.glb` içinde bağımsız NLA track'leri olarak paketlemek
için. Godot 4 `AnimationPlayer` ve Unity `Animator` bu track'leri otomatik
algılar. Standart altı hareket: `idle_combat`, `walk_forward`, `sword_slash`,
`take_damage`, `victory_shout`, `talk_gesture`.

## Kullanılmaz

- **Rigsiz mesh'lerde.** Track paketlemek için kemik gerekir; Trellis çıktısı
  gibi rigsiz mesh'e uygulanamaz (önce K1: riglenmiş temel gövde).
- T-pose ile riglenmiş gövdelerde — K5: T-pose omuz deformasyonunu gizler ve
  auto-rig'i yanıltır; hat A-pose kullanır.
- Altı standart hareket dışında özel hareketler için — şablon sabittir, özel
  hareket ayrı iş.
- Hareketin AI video (Wan) ile sonradan "cilalanacağı" varsayımıyla — K9:
  cila rig animasyonunu atar, paketlenen track'ler orada kaybolur.

## Nasıl çalışır

1. Blender headless `blender_scripts/pack_animations.py` koşar.
2. Her hareket ayrı NLA track olarak eklenir, tek `.glb` export edilir.
3. Girdi: riglenmiş `.blend`/`.glb` + hareket kaynakları. Çıktı: çok track'li `.glb`.

## Doğrulama

```
python test.py
```

Beklenen: çıkış kodu 0. **Test ne ölçüyor, dürüstçe:** yalnızca
`pack_animations.py` dosyasının **var olduğunu**. Paketlemenin çalıştığını,
altı track'in `.glb` içinde olduğunu ya da Godot/Unity'nin onları gördüğünü
ÖLÇMEZ. Bu bir mevcudiyet kontrolüdür, davranış testi değil.

## Sessiz hata riski

**Yüksek.** Test her zaman geçer; paketleme bozulsa da geçer. Gerçek doğrulama
için çıktı `.glb`'nin track adları okunmalı (gltf JSON `animations[].name`)
ve altı standart adla karşılaştırılmalı — yazılmadı. Bu yazılmadan beceri
L0'dan çıkmamalı.
