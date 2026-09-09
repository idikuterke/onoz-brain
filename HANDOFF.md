# HANDOFF — onoz-brain kurulum durumu (2026-09-02, guncelleme 2026-09-09)

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
  - `kutun-arinisi`: 10 regression (%100) + 2 agent gorevi (KA-A05, KA-A07).
    Sette `needs_adjust: true` isaretli gorev KALMADI. KA-10 EMEKLI (asagi bak),
    yerine KA-11 (D-008 kanon bekcisi) eklendi.
  - `gokturk-vision`: 3 regression (%100) - syntax derleme, manifest semasi, workflow dugumleri.
  - `gokturk-verify`: 1 regression (%100) - 38 sinifli kilitli etiket SHA256 degismezlik kontrolu.
- **Baselineler ve Otonomi Kayitlari**:
  - `kutun-arinisi`: PROJE SAGLIGI 10/10 (%100) - `memory/evals/20260909-135952-kutun-arinisi.json`
    (ayni gun 8/10 -> 9/10 -> 10/10). Acik regression kalmadi.
  - `gokturk-vision`: PROJE SAGLIGI 3/3 (%100) - `memory/evals/20260902-120557-gokturk-vision.json`.
  - `gokturk-verify`: PROJE SAGLIGI 1/1 (%100) - `memory/evals/20260902-120609-gokturk-verify.json`.
  - AJAN OTONOMISI: `trial finish` `--solver (cold|assisted|restore)` bayragiyla calisir.
    **ILK SOGUK OLCUM ALINDI (2026-09-09)**: KA-A05 dorduncu cozucu oturumunda sifir
    baglamli olarak cozuldu; `memory/evals/20260909-120257-kutun-arinisi.json`, `kind: agent`.
    (Ilk uc oturum cozucu altyapi hatasiyla dustu, ize birakmadan.) KA-A07 hala
    `agent-restore` olarak durur - otonomi sayilmaz.
  - PROJE SICILI (`brain stats`): 2 gercek kosu (`gokyazi`/`flutter-test-kos`,
    `onoz-brain`/`anonim-export`), %100 otonomi. 10 kosu bariyerine 8 kosu var.
    DIKKAT: eval/trial kayitlari bu sayaci HAREKET ETTIRMEZ; yalniz `brain log` besler.
- **Gorev sirasi**: 1) KA-A07 (TAMAMLANDI - `tests/test_etkilesim_zinciri.gd`, `f8386e2`),
  2) KA-A05 (TAMAMLANDI 2026-09-09 - `tests/test_yelbegen.gd`, `f18f114`; ilk cold olcum,
  uretim kodu degismedi), 3) KA-A06 **IPTAL** - save round-trip ajan gorevi TASARLANMAYACAK.
  Gerekce: 00_CANON/DECISIONS.md D-008 save/load'u ACIKCA yasakliyor ("ajanlarin
  kendiliginden eklemesini engellemek icin"). Boyle bir gorev, ajana kanonu ihlal
  ettirirdi; ayrica kayit formati mimari karardir (README: donguye asla girmeyecekler).
  Yerine KA-11 kanon bekcisi kondu. **Siradaki ajan gorevi bos** - yeni kor nokta
  bulunup tasarlanmali.
- **brain status / activity / dashboard** komutlari calisiyor; pano:
  memory/dashboard.html (tek dosya, offline).
- Lesson kayitlari (2): `20260901-223605-repo-sanity-check.md`,
  `20260909-121745-godot-test-runner.md` (Godot kosusu sonrasi agac kirliligi; iki ayri
  sebep - satir-sonu ve bayat stat kaydi - ayirt etme yontemiyle birlikte).

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
  regression KA-07 gecer; ajan gorevi calismaya devam eder (setup dosyayi
  yine siler). 2026-09-09'da uygulandi: 8 -> 9/10.
- **Remote eklendi (2026-09-09)**: `https://github.com/idikuterke/kutun-arinisi`
  **PRIVATE**. `master` ve `wip/agustos-2026` dallarinin ikisi de push'landi;
  18 gunluk calisma artik tek diskte degil. (`projects.json` remote alani
  tutmaz - motor bunu bilmez, kayit yeri burasidir.)
- **D-008 makineyle korunuyor (2026-09-09)**: KA-11 regression'i
  `evals/kutun-arinisi/helpers/check_no_save_system.gd` ile `scripts/` altini tarar;
  `user://`, `FileAccess.WRITE`, `ResourceSaver`, `store_*` bulursa KALIR. Salt-okur
  erisim mesrudur (DataDB manifest'i READ ile okur) ve isaretlenmez. Mutasyonla
  dogrulandi: game_state.gd'ye sahte `kaydet()` eklenince ihlal satirlariyla KALDI.
- **.gitattributes eklendi (`9b92851`)**: Godot metin kaynaklari eol=lf'e
  sabitlendi, ikili varliklar binary isaretlendi. Renormalizasyon uretmedi.
  Not: bu satir-sonu sebebini cozer, bayat stat kaydi sebebini COZMEZ -
  ayrinti icin godot-test-runner dersi.

## Acik kalemler (kullanici isi)

- **Git Remote Push**: TAMAMLANDI.
  - `onoz-brain`: `https://github.com/idikuterke/onoz-brain` (PUBLIC) - tum gecmis
    ve eval kayitlari GitHub'da.
  - `kutun-arinisi` (Tunga): `https://github.com/idikuterke/kutun-arinisi` (PRIVATE,
    2026-09-09) - master + wip/agustos-2026.
  - KALAN 9 PROJE HALA TEK DISKTE. `gokturk-vision` ve `gokturk-verify` (E: surucusu,
    ikisinin de eval seti var) sıradaki adaylar; her biri ayri gorunurluk karari.
- **STATUS.md Triyaji**: Uykudaki projeler (rota, onoz-idle vb.) panoyu kirletmemek
  icin bos birakilacak; son donemde aktif 5 projenin `Siradaki` satirlari girilecek:
  `kutun-arinisi`, `gokturk-studio`, `onoz-web`, `gokturk-vision`, `gokturk-verify`.
- **Ilk Soguk Olcum (KA-A05)**: TAMAMLANDI (2026-09-09). Dorduncu cozucu oturumu
  sifir baglamli calisti; `--solver cold` ile kaydedildi.
- **KA-A06**: IPTAL EDILDI (D-008). Yeni bir ajan gorevi tasarlanacaksa once mevcut
  kodda gercek bir kor nokta bulunmali; kirmizi cizgi 7 gecerli (tasarlayan cozemez).
- **Sicil Birikimi**: 2/10 kosu. Gercek gelistirmeler sirasinda kosulan testler
  `brain log` ile kaydedilerek bariyer asilacak. Eval ve trial kayitlari bu sayaci
  BESLEMEZ - 2026-09-09 gibi olcum gunleri `brain stats`'i hareket ettirmez.
- Cuma ritueli: `brain activity --days 7 --md --exclude career-ops > memory/haftalik/2026-Wxx.md`
  dosyaya yazilacak sekilde calistirilacak.

## Hizli komutlar

```
brain status                                            # proje tablosu (SAGLIK / OTONOMI ayri)
brain activity --days 30 --exclude career-ops           # commit siniflandirma
brain dashboard --days 30 --exclude career-ops --open   # pano
brain eval kutun-arinisi --kind regression --record     # %90 (9/10)
brain eval gokturk-vision --kind regression --record    # %100 (3/3)
brain eval gokturk-verify --kind regression --record    # %100 (1/1)
brain trial start kutun-arinisi <TASK>                  # iki-fazli ajan denemesi baslat
brain trial finish kutun-arinisi <TASK> --record --solver cold   # soguk otonomi dogrula ve kaydet
```