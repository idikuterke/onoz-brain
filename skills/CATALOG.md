# Beceri haritası — 11 proje

`applies_to` alanı gürültü kontrolüdür. Boş = her projede görünür. Dolu = sadece o tipte.

## Proje kaydı

| Proje | `--type` | Ek etiket |
|---|---|---|
| Kut'un Arınışı | `godot` | gdscript, rpg |
| OnozIdle (Türk Mitolojisi Idle) | `godot` | idle, mobile |
| Gökyazı (YAZGI) | `flutter` | dart, mobile |
| Gökyüzü Günlüğü | `flutter` | dart, offline |
| ONOZ Labs sitesi | `web` | nextjs, ts |
| Göktürk Studio (tamga-ai) | `python-tool` | ml, cv |
| Göktürkçe font üretimi | `python-tool` | fontforge, fonttools |
| Göktürkçe sanal klavye | `web` | static |
| ROTA (Rehberin Adımları) | `flutter` | dart |
| Asimetrik dil oyunu | `web` | game, js |
| career-ops | `python-tool` | automation |

## Beceri katalogu

P0 = ilk kur, P1 = 30 gün içinde, P2 = ihtiyaç doğunca.

### Ortak — `applies_to: []` (11 projede birden)

| Beceri | Doğrulama | Öncelik |
|---|---|---|
| `repo-sanity-check` | build + lint + test tek komutta, exit 0 | **P0** |
| `commit-mesaji-uret` | conventional commit regex'i geçer | P0 |
| `changelog-uret` | son tag'den beri commit'ler CHANGELOG.md'ye, dosya diff'i boş değil | P1 |
| `bagimlilik-denetimi` | outdated/audit çıktısı kritik bulgu içermez | P1 |
| `readme-senkron` | README'deki komutlar gerçekten çalışır | P2 |

### `applies_to: ["godot"]` — 2 proje

| Beceri | Doğrulama | Öncelik |
|---|---|---|
| `godot-scene-smoke-test` | ✅ kurulu | **P0** |
| `godot-test-runner` | `-s res://tests/run_tests.gd` exit 0 | **P0** |
| `godot-asset-import-dogrulama` | `--import` çıktısında kayıp bağımlılık yok | P0 |
| `gdscript-lint` | parse hatası yok | P1 |
| `godot-export-dogrulama` | export preset build üretir, dosya var | P1 |
| `godot-save-roundtrip` | save→load state eşit | P2 |

### `applies_to: ["flutter"]` — 3 proje

| Beceri | Doğrulama | Öncelik |
|---|---|---|
| `flutter-analyze` | `flutter analyze` exit 0 | **P0** |
| `flutter-test-kos` | `flutter test` exit 0 | **P0** |
| `flutter-build-dogrulama` | `flutter build apk --debug` çıktı dosyası var | P1 |
| `l10n-eksik-anahtar` | arb dosyaları arasında eksik anahtar yok | P2 |

### `applies_to: ["web"]` — 3 proje

| Beceri | Doğrulama | Öncelik |
|---|---|---|
| `web-build-dogrulama` | `npm run build` exit 0 | **P0** |
| `link-kontrol` | ölü iç link sayısı = 0 | P1 |
| `bundle-boyut-esigi` | build çıktısı eşiği aşmıyor | P2 |

### `applies_to: ["python-tool"]` — 3 proje

| Beceri | Doğrulama | Öncelik |
|---|---|---|
| `pytest-kos` | `pytest -q` exit 0 | **P0** |
| `ruff-lint` | `ruff check` exit 0 | P1 |
| `cli-smoke` | `--help` exit 0, alt komutlar listeleniyor | P1 |

### `applies_to: ["3d"]` — 3D & Mitoloji Animasyon Becerileri

| Beceri | Doğrulama | Öncelik |
|---|---|---|
| `3d-mesh-temizle` | Blender headless non-manifold onarımı ve 45k decimation | **P0** |
| `3d-animasyon-paketle` | Çoklu NLA track animasyon paketleme | **P0** |
| `3d-viewport-render` | 3 noktalı ışıklandırma ve sinematik kamera yörünge MP4 render | **P0** |
| `3d-wan-video-cila` | ComfyUI Wan 2.1 I2V ile sinematik AI video iyileştirme | **P1** |

### `applies_to: ["asset"]` — etiket, tip değil

Asset pipeline becerileri `--tag asset` ile işaretlenen projelere. Bunlar **P2** — önce build/test hattı otursun.

| Beceri | Doğrulama |
|---|---|
| `blender-headless-export` | çıktı dosyası var, poly sayısı eşik altında |
| `texture-boyut-dogrulama` | boyut 2'nin kuvveti, hedef çözünürlükte |
| `comfyui-batch-uret` | N istendi, N dosya üretildi, hepsi geçerli PNG |

## Kurulum sırası

**P0 = 8 beceri.** İlk hafta bunlar. Hepsi mevcut komutların sarmalayıcısı — yeni şey icat etmiyorsun, `flutter test` zaten var; sisteme kaydettiğin an sicili tutulmaya başlıyor.

P1'e ancak P0'lar 10+ koşu biriktirdikten sonra geç. Aynı anda 25 beceri kurmak sistemin standart ölüm biçimidir.

---

## Kurulum sonrasi gercek durum (2026-09-02)

`SETUP_BRIEF.md` kurulumu tamamlandi; 10 proje `brain link` ile sisteme baglandi:

| Proje | Ekosistem Tipi | Durum |
|---|---|---|
| Kut'un Arinisi | godot (Godot 4.7) | bagli |
| OnozIdle | unity (katalog duzeltildi) | bagli |
| Gokyazi / YAZGI | flutter | bagli |
| Gokyuzu Gunlugu | flutter | bagli |
| ONOZ Labs sitesi | web (Next.js 16) | bagli |
| Gokturk Studio | python-tool (CV/Font) | bagli |
| Gokturk Vision | python-tool (SDXL/ControlNet) | bagli |
| Gokturk Verify | python-tool (VLM OCR/Dataset) | bagli |
| ROTA | flutter | bagli |
| career-ops | web (Node.js) | bagli |

## Meta beceriler — sicili besleyenler

| Beceri | Doğrulama | Ne yapar |
|---|---|---|
| `kos` | `python test.py` (hermetik, 6 davranış) | Beceriyi projede koşturur, sonucu çıkış kodundan alır, `brain log`'u çağırır. `.brain.json`'dan projeyi bulur. Araç yoksa `KOSAMADI` (exit 2) der ve **yazmaz**. |

Kullanım: projenin içinde `kos <beceri>`. `flutter test` yerine `kos flutter-test-kos`.
Kurulum: `%BRAIN_HOME%in` PATH'e eklenir. Godot için `bin/godot.cmd` shim'i
(yerel yol içerir, repoda değil) — `C:\Godot\...console.exe`'ye işaret eder.
