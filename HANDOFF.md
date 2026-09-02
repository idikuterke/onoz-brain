# HANDOFF — onoz-brain kurulum durumu (2026-09-02)

Bu dosya, kurulumu yapan ajanin (AutoCoder) bitis raporudur. Devralan ajan
once bunu, sonra SETUP_BRIEF.md (kurulum sozlesmesi) ve skills/CATALOG.md
sonundaki gercek-durum tablosunu okur.

## Mevcut durum (10 proje bagli, 9 beceri)

- **Sistem kurulu ve calisiyor**: 9 P0 beceri (`brain list`), 10 proje bagli
  (`projects.json`, artik gitignore'da - push guvenli), BRAIN_HOME kalici:
  C:\Users\pc\onozbrain.
- **Bagli Projeler (10 adet)**:
  - `kutun-arinisi` (Godot, C:\Users\pc\Tunga)
  - `gokyazi` (Flutter, C:\Users\pc\YAZGI)
  - `onoz-web` (Next.js/TS, C:\Users\pc\onozlabs)
  - `gokturk-studio` (Python CV/Font, C:\Users\pc\gokturk_studio)
  - `rota` (Flutter, C:\Users\pc\Girisimlerim\Rota)
  - `gokyuzu-gunlugu` (Flutter, C:\Users\pc\tengri_fast_app)
  - `onoz-idle` (Unity, C:\Users\pc\Unity Projeleri\OnozIdle)
  - `career-ops` (Web automation, C:\Users\pc\Documents\antigravity\intelligent-newton)
  - `gokturk-vision` (SDXL/ControlNet, E:\gokturk_vision)
  - `gokturk-verify` (VLM OCR/Dataset, E:\gokturk_verify)
- **Eval setleri**:
  - `kutun-arinisi`: 10 regression (%80) + 2 agent gorevi.
  - `gokturk-vision`: 3 regression (%100) - syntax derleme, manifest semasi, workflow dugumleri.
  - `gokturk-verify`: 1 regression (%100) - 38 sinifli kilitli etiket SHA256 degismezlik kontrolu.
- **Baselineler ve Otonomi Kayitlari**:
  - `kutun-arinisi`: PROJE SAGLIGI 8/10 (%80) - `memory/evals/20260902-094237-kutun-arinisi.json`.
  - `gokturk-vision`: PROJE SAGLIGI 3/3 (%100) - `memory/evals/20260902-120557-gokturk-vision.json`.
  - `gokturk-verify`: PROJE SAGLIGI 1/1 (%100) - `memory/evals/20260902-120609-gokturk-verify.json`.
  - AJAN OTONOMISI: `trial finish` artik `--solver (cold|assisted|restore)` bayragiyla calisir. KA-A07 cozumu git'ten geri alinarak dogrulandigi icin `agent-restore` olarak kayda gecirildi (OTONOMI tablosunda soguk olcum bekleniyor `-`).
  - PROJE SICILI (`brain stats`): 1 gercek kosu (`gokyazi` / `flutter-test-kos`), %100 otonomi, 3 dk inceleme.
- **Gorev sirasi**: 1) KA-A07 (TAMAMLANDI - `tests/test_etkilesim_zinciri.gd` yazildi, mutasyon kanitlandi ve Tunga'ya commit'lendi `f8386e2`), 2) KA-A05 (Yelbegen testi - ilk gercek cold otonomi olcumu olacak), 3) KA-A06 (save round-trip).
- **brain status / activity / dashboard** komutlari calisiyor; pano:
  memory/dashboard.html (tek dosya, offline).
- Lesson kaydi: memory/lessons/20260901-223605-repo-sanity-check.md.

## Kirmizi cizgiler (devralan ajan bunları ihlal etmez)

1. **brain.py'yi DEGISTIRME** - hata bulursan raporla.
2. **Bu ajanin kalibrasyonlarini ezme**: upstream paketleri artik SADECE
   brain.py icerir (upstream taahhudu). Eski tarz cok-dosyali paket gelirse
   tasks.jsonl, break.py, CATALOG.md, skills/*/test.py uzerine YAZMA -
   mevcutlarini koru, yalniz brain.py'yi al.
3. **Sahte sicil yok**: `brain log` ile deneme kaydi yazilmaz. `brain stats`
   0 kosu gostermeli.
4. **Verify gevsetilmez**; eval seti dondurulur (AGENT_EVAL_SPEC.md).
5. **Kirli agacta ajan gorevi kosmaz** (motor engeller); untracked kalinti
   varsa --allow-dirty yalniz gerekceli kullanilir.
6. Proje kaynak dosyalarina .brain.json disinda yazilmaz; istisna: ajan
   gorevlerinin kendisi (KA-A05/A07 test dosyalari) - teardown'lari kontrol
   altindadir.
7. **Gorevi tasarlayan oturum o gorevi cozmez (olcum kirlenmesi)**: Sinavi yazan
   sinava giremez. KA-A07 ve benzeri ajan gorevleri, sadece `brain context`
   brifingi alan AYRI ve temiz bir oturumda cozdurulur. Tasarimci oturum yalnizca
   olcum (setup / eval / teardown) tarafinda kalir.
8. **Ozellik Dondurma (Feature Freeze - 10 kosu bariyeri)**: `brain stats` en az
   10 gercek kosuya ulasana kadar `brain.py`'ye YENI OZELLIK EKLENMEZ. Yalnizca
   hata duzeltmesi yapilabilir. Sistem kendini besleyecek veri birikmeden
   motor olcecegi isten hizli buyutulmez.

## Tunga (kutun-arinisi) ozel durumu

- Proje yolu C:\Users\pc\Tunga (project.godot name="KutunArinisi", Godot
  4.7.1 - C:\Godot\Godot_v4.7.1-stable_win64_console.exe, PATH'te degil).
- **18 gunluk calisma guvenceye alindi**: `stash@{0}` basariyla `wip/agustos-2026`
  dalina cevrildi ve commit'lendi (`bcf37fb`). `master` dali tertemiz. Eval
  kosulari master'da calisir, calisma devam edeceginde `git checkout wip/agustos-2026`.
- **CONVENTIONS.md olusturuldu ve commit'lendi (`2be68e1`)**: Dizin yapisi, test
  kalibi (`res://tests/run_tests.tscn` ve otomatik test kesfi), EventBus ve
  autoload mimarisi, test izolasyonu (`GameState.sifirla()`) kurallari belgelendi.
  Ajan brifingi artik sifir-baglamli ajanlar icin tam ve ogrenmeye hazir.
- Ajan gorevleri test yazinca: iyi test **projeye commit edilir** ->
  regression KA-07 gecer (8 -> 9/10); ajan gorevi calismaya devam eder
  (setup dosyayi yine siler).

## Acik kalemler (kullanici isi)

- Git remote verilmeli -> `git push` (public olacak; eval kayitlari otonomi
  egrisinin kaniti).
- STATUS.md icerikleri (10 proje x 2 satir: Siradaki ve Engel). Ajan commit
  gecmisinden "Durum" satirini taslak olarak 10 projeye yazdi; Siradaki ve
  Engel satirlarini kullanici dolduracak.
- Cuma ritueli: `brain activity --days 7 --md --exclude career-ops > memory/haftalik/2026-Wxx.md`
  dosyaya yazilacak sekilde calistirilacak.

## Hizli komutlar

```
brain status                                            # proje tablosu (SAGLIK / OTONOMI ayri)
brain activity --days 30 --exclude career-ops           # commit siniflandirma
brain dashboard --days 30 --exclude career-ops --open   # pano
brain eval kutun-arinisi --kind regression --record     # %80 (8/10)
brain eval gokturk-vision --kind regression --record    # %100 (3/3)
brain eval gokturk-verify --kind regression --record    # %100 (1/1)
brain trial start kutun-arinisi <TASK>                  # iki-fazli ajan denemesi baslat
brain trial finish kutun-arinisi <TASK> --record --solver cold   # soguk otonomi dogrula ve kaydet
```