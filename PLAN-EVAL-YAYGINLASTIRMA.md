# Plan — eval setlerini diğer projelere yaygınlaştırma

> Hazırlandı: 2026-09-09. Üç bağımsız ajan oturumuna verilmek üzere.
> Her brif kendi başına yeterlidir; ajanlar birbirini beklemez, birbirinin
> dosyasına dokunmaz.

## Bugünkü gerçek durum

11 bağlı projeden **yalnızca 3'ünde** eval seti var:

| Proje | Tip | Eval | Durum |
|---|---|---|---|
| kutun-arinisi | godot | 10 regression + 3 agent | referans örnek, 10/10 |
| gokturk-vision | python-tool | 3 regression | 3/3 |
| gokturk-verify | python-tool | 1 regression | 1/1 |
| gokyazi | flutter | **yok** | aktif (20 saat önce commit) |
| gokyuzu-gunlugu | flutter | **yok** | aktif, 18 dart testi hazır |
| onoz-web | web | **yok** | aktif (27 saat) |
| gokturk-studio | python-tool | **yok** | aktif (27 saat) |
| onoz-idle | unity | **yok** | 3 gün |
| rota | flutter | **yok** | uykuda (4 ay) |
| career-ops | web | **yok** | raporlarda hariç tutuluyor |

Not: "gökyazı gibi" hedefi yanıltıcı — Gökyazı'da da eval seti yok; orada
yalnızca `.brain.json` + `STATUS.md` + 1 koşu sicili var. **Tek tam örnek Tunga'dır.**

## Hedef durum (proje başına)

1. `.brain.json` — bağlama işareti (hepsinde var, iş yok)
2. `STATUS.md` — üç satır, dolu ve güncel
3. **`evals/<proje>/tasks.jsonl` — `kind: regression` görevler** ← asıl boşluk
4. Kaydedilmiş baseline (`brain eval <proje> --kind regression --record`)
5. `CONVENTIONS.md` — sıfır bağlamlı ajan brifingi (şimdilik yalnız Tunga'da)

## Kapsam DIŞI (üç ajan da yapmayacak)

- **`kind: agent` görevi tasarlamak.** Önce sağlık taban çizgisi oturur.
  Ajan görevleri ayrı bir turda, kırmızı çizgi 7 ile (tasarlayan çözemez).
- **`brain.py`'ye dokunmak.** Özellik Dondurma: `brain stats` 10 koşuya
  ulaşana kadar yeni özellik eklenmez. Hata bulursan raporla, düzeltme.
- **`brain log` yazmak.** Sicil yalnız gerçek doğrulanmış koşularla, kullanıcı
  tarafından beslenir. Ajan sicil yazmaz.
- Hedef projenin kaynak dosyalarını değiştirmek. Eval seti kodu **ölçer**, düzeltmez.

---

# Bugün öğrenilen, tekrarlanmaması gereken hatalar

Bunlar 2026-09-09'da Tunga'da bizzat yaşandı. Üçünün de okuması zorunlu.

**1. Görev, projenin kendi kararlarına aykırı olmasın.**
KA-10 "kayıt/yükleme round-trip" ölçüyordu. Meğer projenin kanonunda
`D-008 — Save/load yok` kararı varmış, gerekçesi de *"ajanların kendiliğinden
eklemesini engellemek"*. Yani görev hiç var olmayacak bir özelliği bekliyordu ve
sonsuza kadar kalacaktı. **Görev yazmadan önce projenin karar/kanon belgelerini
oku** (`DECISIONS.md`, `AGENTS.md`, `CLAUDE.md`, `README`). Reddedilmiş bir
özelliği ölçen görev, sağlığı kalıcı olarak yanlış gösterir.

**2. `verify` gerçek proje bağlamında koşmalı.**
KA-07 testi `godot -s dosya.gd` ile tek başına koşuyordu; o modda autoload'lar
yüklenmiyor ve `GameState` bulunamıyordu — test dosyası yazılsa bile görev
geçemezdi. Genel kural: doğrulama komutu projenin **normalde koştuğu** giriş
noktasını kullanmalı (suite sahnesi, `flutter test`, `npm test`, `pytest`),
tek dosyayı izole koşan kestirmeleri değil.

**3. Görevi eklemeden önce KALDIĞINI kanıtla.**
`AGENT_EVAL_SPEC` kırmızı çizgi 1. Ölçtüğü şey yokken görev geçiyorsa, o görev
hiçbir şey ölçmüyordur. Her yeni görev için: hedefi geçici olarak boz/kaldır →
`brain eval <proje> --task <ID>` → **KALDI** gör → geri al. `--record` verme.

**4. `teardown` ağacı temiz bırakmalı.**
Ajan üretim kodunu da değiştiriyorsa dosya silmek yetmez; `git checkout -- <yol>`
gerekir. Koşu sonrası `git status --porcelain` boş olmalı.

**5. Yol biçimi.**
`tasks.jsonl` içinde yardımcı script yollarında **eğik çizgi** kullan
(`%BRAIN_HOME%/evals/_helpers/break.py`). Ters eğik çizgili `\break.py` bir
yerde backspace karakterine dönüşüp komutu bozuyor.

**6. Ağaç kirliliğini teşhis et, körlemesine temizleme.**
`git status` M gösterip `git diff` boşsa bu bayat stat kaydıdır, gerçek
değişiklik değil; `git add -A` tazeler ve hiçbir şey stage'lemez.

---

# AJAN 1 — Flutter hattı

**Kapsam (3 proje)**
- `gokyuzu-gunlugu` — `C:\Users\pc\tengri_fast_app` (18 dart testi hazır, aktif)
- `gokyazi` — `C:\Users\pc\YAZGI` (1 dart testi, aktif)
- `rota` — `C:\Users\pc\Girisimlerim\Rota` (uykuda, 4 ay) → **minimal set yeter**

**Teslim edilecekler**
1. `evals/gokyuzu-gunlugu/tasks.jsonl`, `evals/gokyazi/tasks.jsonl`,
   `evals/rota/tasks.jsonl` — hepsi `kind: regression`.
2. Her proje için kaydedilmiş baseline.
3. `STATUS.md` üç satırı güncel (uykudaki `rota` için boş bırakılabilir).

**Önerilen görevler** (uyarlayarak kullan, körü körüne kopyalama)
- `flutter analyze` temiz çıkar — `flutter-analyze` becerisi
- `flutter test` tamamen geçer — `flutter-test-kos` becerisi
- `flutter pub get` hatasız çözümlenir
- 18 testi olan `gokyuzu-gunlugu` için: belirli bir kritik testin **adıyla**
  geçtiğini doğrulayan bir görev (Tunga'daki `--require-line` deseninin karşılığı)

**Dikkat:** `rota` 4 aydır dokunulmamış; `flutter analyze` bugün büyük olasılıkla
kalır. Bu **normaldir ve gizlenmez** — baseline dürüst kaydedilir. Düşük skor
projenin gerçek durumudur; skoru güzelleştirmek için görev gevşetme.

---

# AJAN 2 — Web + Unity

**Kapsam (2 proje)**
- `onoz-web` — `C:\Users\pc\onozlabs` (Next.js 16 / TS, aktif)
- `onoz-idle` — `C:\Users\pc\Unity Projeleri\OnozIdle` (Unity, 3 gün)

**Teslim edilecekler**
1. `evals/onoz-web/tasks.jsonl` + baseline
2. `evals/onoz-idle/tasks.jsonl` + baseline **veya** aşağıdaki rapor
3. İki `STATUS.md` güncel

**onoz-web için önerilen görevler**
- `npm run lint` temiz (kökte `eslint.config.mjs` var)
- `npm run build` hatasız üretir — `web-build-dogrulama` becerisi
- `package.json` script'lerini **önce oku**; hangi komutların gerçekten var
  olduğunu varsayma.

**onoz-idle (Unity) — en zor kalem, dürüst ol**
Unity headless test koşumu (`-runTests -batchmode`) Editor yolu ve lisans
gerektirir. Makinede bunlar **doğrulanmadan** görev yazma. Koşturamıyorsan:
- Koşturulabilen ne varsa onu ölç (asset/`.meta` eşleşmesi, `ProjectSettings`
  şeması gibi Unity gerektirmeyen kontroller),
- `tasks.jsonl` yerine kısa bir rapor yaz: neyin neden koşturulamadığı.

**Koşturulamayan bir komutu görev diye eklemek, bugün KA-07'de yaptığımız
hatanın aynısıdır.** Boş set, yalancı setten iyidir.

---

# AJAN 3 — Python-tool hattı + tutarlılık denetimi

**Kapsam**
- `gokturk-studio` — `C:\Users\pc\gokturk_studio` (eval yok, aktif)
- Mevcut iki setin denetimi: `evals/gokturk-vision/`, `evals/gokturk-verify/`

**Teslim edilecekler**
1. `evals/gokturk-studio/tasks.jsonl` + baseline
2. `evals/DENETIM-2026-09.md` — mevcut iki set için denetim raporu. Her görev
   için üç soruya cevap:
   - bugün gerçekten koşuyor mu?
   - izole koşum tuzağı var mı (madde 2)?
   - ölçtüğü şey ortadan kalkınca KALIYOR mu?

   Bulduğun kusurları **raporla, tek başına düzeltme** — kalibrasyon kullanıcı onayıyla.

**gokturk-studio için dikkat**
Kök dizin dağınık: `.py` dosyaları, HTML/PDF çıktıları, `inputs/`,
`gokturk_pipeline_v2/` bir arada; `pyproject.toml` ve `tests/` **yok**. Yani
`pytest -q` bugün muhtemelen koşmaz. Önce yapıyı incele, ölçülebilir gerçek bir
şey bul — script'lerin import edilebilirliği, ya da `gokturk_labels_v1_locked.json`
gibi kilitli veri dosyalarının SHA256 değişmezliği (`gokturk-verify` setinde
bunun çalışan bir örneği var). Test altyapısı kurmak senin işin değil;
**var olanı ölç.**

---

# Üçünün de uyacağı kırmızı çizgiler

1. `brain.py` DEĞİŞTİRİLMEZ. Hata bulursan raporla.
2. `brain log` yazılmaz. Sahte sicil yok.
3. Mevcut `evals/kutun-arinisi/` setine dokunulmaz.
4. Görev eklemeden önce "ölçtüğü şey yokken KALIYOR mu" kanıtlanır.
5. Koşu sonrası hedef projenin ağacı temiz bırakılır (`git status --porcelain` boş).
6. Baseline dürüst kaydedilir; düşük skor gizlenmez, görev gevşetilmez.
7. Projenin kendi karar/kanon belgeleri okunmadan görev yazılmaz.

# Kullanıcının kabul kontrolü

Her ajan bitirdiğinde:

```
brain eval <proje> --kind regression        # kaydetmeden gör
brain status                                # tabloya girdi mi
cd <proje> && git status --porcelain        # bos olmali
```

Ve her yeni görev için tek soru: **"bu görev, ölçtüğü şey ortadan kalkınca
kalıyor mu?"** Cevap hayırsa görev geri çevrilir.
