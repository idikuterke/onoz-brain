# repo-sanity-check

> Beceri kimliği: `repo-sanity-check` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Herhangi bir projede (godot, flutter, web, python-tool) iş bitmeden önce build + lint + test
hattının tamamını tek komutta koşup "geçti/kaldı" kararı vermek için; proje tipi marker
dosyalarından otomatik çıkarılır, tipine göre `godot --import`/`godot -s run_tests.gd`,
`flutter analyze`/`flutter test`, `npm run lint`/`npm run build`/`npm test` veya
`pytest -q` zinciri sırayla koşulur ve atlanan adımlar gerekçesiyle raporlanır.

## Kullanılmaz

- Tek bir alt komutu izole koşmak için — o işin kendi becerisi var (flutter-test-kos,
  pytest-kos, web-build-dogrulama...); bu beceri toparlayıcıdır, tekrar değildir.
- Proje tipinin marker dosyasıyla tespit edilemediği, araçların kurulu olmadığı durumlarda
  "geçti" beklentisiyle — araç yoksa adım ATLANDI değil, sonuç 2 (ön koşul) olur.
- Kod kalitesi yargısı (kod incelemesi) için — bu beceri mekanik doğrulamadır, yorum üretmez.

## Nasıl çalışır

1. `--project` dizininden tip tespiti: `project.godot` → godot, `pubspec.yaml` → flutter,
   `package.json` → web, `pyproject.toml`/`setup.*`/`pytest.ini`/`tests/` → python-tool.
2. Tipe göre zincir kurulur; her adım ya `ready` ya "araç yok" ya "bu projede yok" etiketlidir.
3. `ready` adımlar sırayla koşulur; çıktının son satırları hatada bastırılır.
4. Sonuç: kalan adım varsa 1, araç eksik adım varsa 2, hiç adım uygulanamıyorsa 2, değilse 0.

## Doğrulama

```
python test.py --project <proje-yolu>
```

Beklenen: çıkış kodu 0; çıktıda `[ gecti ]` adımlar, `[arac_yok]`/`[  yok  ]` atlananlar.

## Sessiz hata riski

Var ve iki yüzlü. (1) "Geçti" çıktısı okunurken atlanan adımları saymadan geçmek tehlikelidir:
test/ dizini veya test script'i olmayan bir projede test adımı `yok` etiketiyle atlanır ve sonuç
yine 0 dönebilir — "geçti" burada "koşulabilecek her şey koştu ve geçti" demektir, "test edildi"
değil. (2) Build adımı çıktı dosyasını hiç kontrol etmez: `npm run build` başarılı çıkıp boş
`dist/` üretebilir; bu test çıktının içeriğine bakmaz. Araç eksikse sonuç zaten 2'dir ama
tek araçlı zincirde diğer adımlar sessizce `yok` sayılabileceğinden, 0 okuyan biri eksik
kapsamı gözden kaçırabilir.
