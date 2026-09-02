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
- **18 gunluk calisma guvenceye alindi**: `stash@{0}` basariyla `wip/agustos-2026`
  dalina cevrildi ve commit'lendi (`bcf37fb`). `master` dali tertemiz. Eval
  kosulari master'da calisir, calisma devam edeceginde `git checkout wip/agustos-2026`.
- Ajan gorevleri test yazinca: iyi test **projeye commit edilir** ->
  regression KA-07 gecer (8 -> 9/10); ajan gorevi calismaya devam eder
  (setup dosyayi yine siler).

## Acik kalemler (kullanici isi)

- Git remote verilmeli -> `git push` (public olacak; eval kayitlari otonomi
  egrisinin kaniti).
- STATUS.md icerikleri (8 proje x 2 satir: Siradaki ve Engel). Ajan commit
  gecmisinden "Durum" satirini taslak olarak 8 projeye yazdi; Siradaki ve
  Engel satirlarini kullanici dolduracak.
- Cuma ritueli: `brain activity --days 7 --md --exclude career-ops > memory/haftalik/2026-Wxx.md`
  dosyaya yazilacak sekilde calistirilacak.

## Hizli komutlar

```
brain status                                            # proje tablosu (SAGLIK / OTONOMI ayri)
brain activity --days 30 --exclude career-ops           # commit siniflandirma
brain dashboard --days 30 --exclude career-ops --open   # pano
brain eval kutun-arinisi --kind regression --record     # %80 (8/10)
brain eval kutun-arinisi --kind agent --record          # %0 (0/2, yukseltilecek sayi)
```