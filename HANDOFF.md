# HANDOFF — onoz-brain kurulum durumu (2026-09-02)

Bu dosya, kurulumu yapan ajanin (AutoCoder) bitis raporudur. Devralan ajan
once bunu, sonra SETUP_BRIEF.md (kurulum sozlesmesi) ve skills/CATALOG.md
sonundaki gercek-durum tablosunu okur.

## Mevcut durum (8 commit, hepsi yerel - remote yok)

- **Sistem kurulu ve calisiyor**: 9 P0 beceri (`brain list`), 8 proje bagli
  (`projects.json`, artik gitignore'da - push guvenli), BRAIN_HOME kalici:
  C:\Users\pc\onozbrain.
- **Eval seti** (evals/kutun-arinisi/tasks.jsonl, 12 gorev):
  - 10 regression (Windows'a kalibre edildi; bash sozdizimi cmd'de
    calismaz - DOKUNMA) + 2 agent gorevi.
  - evals/_helpers/godot_task.py: ortak Windows kosucu (exit 0/1/2/3;
    --require-line = sessiz-hata kapani).
  - evals/_helpers/break.py: deterministik bozma kancalari (Tunga'ya
    kalibre; her kancanin kaniti dosya basindaki notlarda).
- **Baselineler** (memory/evals/*.json): PROJE SAGLIGI 8/10 (%80) -
  20260902-094237; AJAN OTONOMISI 0/2 (%0) - 20260902-100844.
  Yukseltilecek sayi ajan otonomisi.
- **Gorev sirasi** (upstream karari): 1) KA-A07 (etkilesim zinciri mutasyon
  testi), 2) KA-A05 (Yelbegen testi), 3) KA-A06 (save round-trip - henuz
  yazilmadi). KA-A01 ancak KA-A07 kapatildiktan sonra eklenebilir (kor
  nokta: npc-signal bozmasi mevcut paketle yakalanmiyor - kaniti break.py
  notlarinda).
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

## Tunga (kutun-arinisi) ozel durumu

- Proje yolu C:\Users\pc\Tunga (project.godot name="KutunArinisi", Godot
  4.7.1 - C:\Godot\Godot_v4.7.1-stable_win64_console.exe, PATH'te degil).
- **stash@{0}: kullanicinin 18 gunluk commit'lenmemis calismasi** ("18 gunluk
  calisma - eval oncesi"). Geri verme: `git stash pop`. Kullanici
  gelistirmeye devam etmeden once stash'i pop'lamali/commit'lemeli; eval
  kosumlari sirasinda stash durmali.
- Ajan gorevleri test yazinca: iyi test **projeye commit edilir** ->
  regression KA-07 gecer (8 -> 9/10); ajan gorevi calismaya devam eder
  (setup dosyayi yine siler).

## Acik kalemler (kullanici isi)

- Git remote verilmeli -> `git push` (public olacak; eval kayitlari otonomi
  egrisinin kaniti).
- C:\Users\pc\Desktop\gokyazi\.brain.json silinecek (eski konum kalintisi).
- STATUS.md icerikleri (8 proje x 3 satir: nerede kaldim / siradaki adim /
  engel) - yalniz kullanicinin bildigi veri; sablon:
  `brain status --template > <proje>\STATUS.md`.
- Opsiyonel: cuma ritueli icin `brain activity --days 7 --md` zamanlanmis gorev.

## Hizli komutlar

```
brain status                      # proje tablosu
brain activity --days 30          # commit siniflandirma
brain dashboard --open            # pano
brain eval kutun-arinisi --kind regression --record   # ~%100 beklenir
brain eval kutun-arinisi --kind agent --record        # yukseltilecek sayi
brain eval kutun-arinisi --kind agent --record --allow-dirty  # untracked kalinti varsa
```