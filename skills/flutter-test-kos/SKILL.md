# Flutter test koşu

> Beceri kimliği: `flutter-test-kos` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Bir Flutter projesinde `test/` altındaki birim ve widget testlerini `flutter test` ile
koşup geçti/kaldı kararı vermek için; feature bittiğinde, merge/export öncesinde ve
repo-sanity-check zincirinin flutter ayağında analyze'den sonra çalıştırılır.

## Kullanılmaz

- Statik analiz için — o iş `flutter-analyze`'ın; bu beceri kod koşar.
- Gerçek cihaz/emülatör veya entegrasyon testi için — `flutter test` headless sanal
  ortamda koşar; cihaz davranışı, ağ ve performans bu testin kapsamı değildir.
- `test/` altında `*_test.dart` olmayan projede — exit 2 döner; "geçti" uydurulmaz.

## Nasıl çalışır

1. `flutter` PATH'te aranır, `pubspec.yaml` kontrol edilir, `test/` altında en az bir
   `*_test.dart` aranır — eksikse ön koşul (2).
2. `flutter test` proje dizininde (cwd) koşulur.
3. Çıkış kodu 0 → geçti; 0 dışı → çıktının son 25 satırı basılıp KALDI.

## Doğrulama

```
python test.py --project <flutter-proje-yolu>
```

Beklenen: çıkış kodu 0.

## Sessiz hata riski

Var. (1) Testlerin assertion'ları zayıf olabilir: yalnızca "widget render oldu" diyen boş
testler çıkış kodu 0 üretir ve mantık hatasını görmez — bu beceri test kalitesini ölçmez,
sadece koşar. (2) `skip:` işaretli testler koşulmaz ama raporda görünür; sürekli skip'li
bir test fiilen ölüdür ve bu beceri onu "kaldı" saymaz. (3) İlk koşu `pub get`'i örtük
çağırabilir; çevrimdışı makinede bu KALDI olarak görünür — neden araç değil ortam.
