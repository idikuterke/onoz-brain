# Flutter statik analiz

> Beceri kimliği: `flutter-analyze` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Bir Flutter/Dart projesinde `flutter analyze`'un temiz çıktığını — yani error, warning ve
info seviyesinde analyzer sorunu kalmadığını — doğrulamak için; her commit öncesi geçiş
kapısıdır ve repo-sanity-check zincirinin flutter ayağının ilk adımıdır.

## Kullanılmaz

- Test koşmak için — o iş `flutter-test-kos`'un; analyze statiktir, test çalıştırmaz.
- Otomatik düzeltme için — analyze yazar, düzeltmez; `dart fix` ayrı bir iştir.
- Cihaz/emülatör davranışı için — analyzer derlemez, koşmaz.

## Nasıl çalışır

1. `flutter` PATH'te aranır (`--flutter` ile yol verilir), `pubspec.yaml` varlığı
   kontrol edilir — yoksa ön koşul (2).
2. `flutter analyze` proje dizininde (cwd) koşulur.
3. Çıkış kodu 0 → temiz; 0 dışı → sorun listesinin son 25 satırı basılıp KALDI.

## Doğrulama

```
python test.py --project <flutter-proje-yolu>
```

Beklenen: çıkış kodu 0.

## Sessiz hata riski

Var. (1) `analysis_options.yaml` içindeki `exclude:` bölümlerine giren dosyalar analyzer'a
görünmez — hatalı dosyanın dışlandığı bir projede analyze "temiz" çıkar; yeni dosya
eklerken exclude listesine takılıp takılmadığına bak. (2) Bağımlılıklar indirilmemişse
(`pub get` koşulmamışsa) analyze `package:...` URI'lerini bulamayıp sahte hata fırtınası
üretir — bu KALDI'dır (yanlış yönde kalır, güvenli taraf) ama nedeni araç değil ortamdır;
çözüm `flutter pub get`, beceriyi gevşetmek değil.
