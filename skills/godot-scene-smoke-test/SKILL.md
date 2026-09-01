# Godot sahne duman testi

> Beceri kimliği: `godot-scene-smoke-test`

## Ne zaman kullanılır

Bir Godot sahnesi (.tscn) eklendiğinde veya değiştirildiğinde, sahnenin headless
modda hatasız yüklenip yüklenmediğini doğrulamak için. Sprint sonu build öncesi
zorunlu geçiş kapısı.

## Kullanılmaz

- Oynanış dengesi, "oyun eğlenceli mi" gibi öznel yargılar için — ölçülemez.
- Görsel/asset kalitesi denetimi için — bu test piksele bakmaz.
- Editör içi (headless olmayan) davranışları test etmek için.

## Nasıl çalışır

1. `godot --headless --quit-after 2 --path <proje> <sahne.tscn>` çalıştırılır.
2. Çıktıda `SCRIPT ERROR`, `ERROR:`, `Parse Error` veya `Failed to load` aranır.
3. Bulunursa test kalır; çıkış kodu 0 dışı döner.

## Doğrulama

```
python test.py --project <godot-proje-yolu> --scene <sahne.tscn>
```

Beklenen: çıkış kodu 0, hata satırı yok.

## Sessiz hata riski

Var. Sahne yüklenir ama node referansı runtime'da null olabilir; duman testi bunu
yakalamaz. Bu yüzden bu beceri tek başına L2'ye çıkarılmamalı — yanına oynanış
smoke testi gerekir.
