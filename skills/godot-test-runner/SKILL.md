# Godot test koşucu

> Beceri kimliği: `godot-test-runner` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Bir Godot projesinde GDScript test paketini (`res://tests/run_tests.gd`) headless modda
koşup geçti/kaldı kararı vermek için; feature bittiğinde, merge/export öncesinde ve
repo-sanity-check zincirinin godot ayağı olarak çalıştırılır.

## Kullanılmaz

- Sahne yükleme sağlığı için — o iş `godot-scene-smoke-test`'in; bu beceri test script'i koşar.
- Test script'i hiç yazılmamış projede — exit 2 döner; boş gezen "test geçti" uydurulmaz,
  önce script yazılır.
- Editör içi / görsel davranış testi için — headless koşar, render ve input beklemesi görmez.

## Nasıl çalışır

1. `godot` PATH'te aranır (`--godot` ile yol verilir); `project.godot` ve test script'i
   dosya sistemi üzerinde var mı diye bakılır — yoksa ön koşul (2).
2. `godot --headless --path <proje> -s res://tests/run_tests.gd` koşulur.
3. Karar iki ayaklı: çıkış kodu 0 **ve** çıktıda `SCRIPT ERROR`/`ERROR:`/`Parse Error`/
   `Failed to load`/`Assertion failed` marker'ı yok.

## Doğrulama

```
python test.py --project <godot-proje-yolu>
```

Beklenen: çıkış kodu 0, hata satırı yok.

## Sessiz hata riski

Var, iki yönlü. (1) Godot bazı script hatalarında süreç çıkış kodunu yine 0 bırakır; bu yüzden
çıktı da taranır. Ama marker listesi statiktir: yeni/farklı biçimli bir hata mesajı listeye
değilse geçti sayılır. (2) Test script'inin kendisi zayıfsa (assert'i try/except ile yutan,
hatayı yazıp exit 0 dönen bir script) bu sarmalayıcı onu kurtaramaz — "temiz koştu" yalnızca
"script kendi standardına göre temiz" demektir. Script'in hatada sıfırdan dönmesi proje
tarafının sorumluluğudur.
