# Godot asset import doğrulama

> Beceri kimliği: `godot-asset-import-dogrulama` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Projeye asset/scene/resource eklendikten veya depo clone edildikten sonra headless
`--import`'un temiz çıktığını — yani kayıp resource, açılamayan dosya veya loader'sız
asset kalmadığını — doğrulamak için; build/export öncesi geçiş kapısıdır.

## Kullanılmaz

- Godot 3 projelerinde — `--import` bayrağı Godot 4+'a aittir; Godot 3 "Unknown command
  line argument" ile düşer ve bu test KALDI der (araç bozuk değil, sürüm uymuyor).
- Asset kalitesi/boyut/çözünürlük denetimi için — sadece yüklenebilirliğe bakar, piksele değil.

## Nasıl çalışır

1. `godot` PATH'te aranır, `project.godot` varlığı kontrol edilir — yoksa ön koşul (2).
2. `godot --headless --path <proje> --import` koşulur (ilk import uzun sürebilir).
3. Çıktı şu kalıplar için taranır: `Failed to load`, `Cannot open file`, `Could not find
   type`, `No loader found`, `Error importing`, `Parse Error`, `SCRIPT ERROR`,
   `missing dependency`; çıkış kodu 0'dan dönerse de KALDI sayılır.

## Doğrulama

```
python test.py --project <godot-proje-yolu>
```

Beklenen: çıkış kodu 0, kayıp bağımlılık satırı yok.

## Sessiz hata riski

Var. Marker listesi statiktir: Godot'un gelecek sürümlerinde veya farklı bir hata kalıbında
görülen "kaynak bulunamadı" mesajı listeye yoksa import geçti sayılır — yeni bir kalıp
görüldüğünde listeye eklenmeli. Ayrıca ikinci koşu `.godot/` cache'i ısındığı için bazı
hataları yeniden üretmeyebilir; en bilgilendirici çıktı ilk import'undur, cache silinmeden
koşulan tekrar "temiz" çıktısı yanıltabilir.
