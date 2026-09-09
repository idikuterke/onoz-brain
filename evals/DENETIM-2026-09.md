# Denetim Raporu — evals/gokturk-vision + evals/gokturk-verify (2026-09-09)

> Denetleyen: AutoClaw ana oturumu (AJAN 3 kapsamı, kullanıcı planı uyarınca).
> Kural: kusurlar RAPORLANIR, tek başına düzeltilmez — kalibrasyon Han onayıyla.
> Kanıt dayanağı: 2026-09-09 koşum kayıtları (memory/evals/20260909-161443-gokturk-studio.json
> + bugünkü kayıtsız koşumlar) ve görev dosyalarının satır satır okunması.

## 1. gokturk-vision (GV-01..GV-03) — bugün 3/3 koşuyor

| Görev | Bugün koşuyor mu? | İzole koşum tuzağı (madde 2)? | KALDI kanıtı (madde 3)? |
|---|---|---|---|
| GV-01 kök .py derleme | ✅ evet (3/3 içinde) | ✅ yok — cwd=proje kökü, harici servis gerektirmiyor | ❌ bekliyor: kökte geçici bozuk .py ile mutasyon koşumu yapılmadı |
| GV-02 manifest şeması | ✅ evet | ✅ yok — tek bağımlılık `inputs/manifest.json` varlığı | ❌ bekliyor: manifest'i geçici bozup `--task GV-02` koşumu yapılmadı |
| GV-03 workflow grafı | ✅ evet | ✅ yok — yalnız JSON okuma + referans denetimi | ❌ bekliyor: workflow'da geçici boş referans ekleyip koşum yapılmadı |

**Bulgu G-1 (önem: orta):** GV-01 yalnızca **kök dizindeki** `*.py` dosyaları derler
(`Path('.').glob('*.py')`). gokturk-vision'da `core/qa_gate.py`, `core/conformer.py`
gibi alt dizin scriptleri varsa bunlar ölçülmüyor. GS-02'nin aksine rglob kullanmıyor.
Çözüm önerisi (onayla uygulanır): rglob'a çevirmek veya `__pycache__` filtresiyle alt
dizinleri kapsamak.

**Bulgu G-2 (önem: düşük):** GV-02 manifest'i yalnızca `id` + `prompt` varlığıyla
doğruluyor — şema denetimi sığ. Bir `schema.json` alan listesiyle genişletilebilir
(onayla).

## 2. gokturk-verify (GVER-01) — bugün 1/1 koşuyor

| Görev | Koşuyor mu? | Tuzak? | KALDI kanıtı? |
|---|---|---|---|
| GVER-01 kilitli etiket SHA256 | ✅ evet | ✅ yok | ⚠️ doğrudan değil — **eşdeğerlik yoluyla**: aynı dosyanın gokturk-studio kopyası üzerinde GS-01 ile bugün bizzat kanıtlandı (KALDI exit=1 → byte-aynı geri alma → SHA256 eşleşti → exit=0). E:\gokturk_verify kopyasında doğrudan mutasyon koşumu yapılmadı. |

**Bulgu V-1 (pozitif):** GS-01 ile GVER-01 aynı kilitli şemayı (aynı beklenen
hash `2c6c77b8…85a5`) iki depoda birlikte koruyor — zincir bütünlüğü iyi kurulu.
İki görevin de hash'i aynı olduğu sürece tek dosyadan çift depo doğrulaması geçerli.

## 3. gokturk-studio (GS-01..GS-03) — yeni set, bugün 3/3 baseline

| Görev | KALDI kanıtı |
|---|---|
| GS-01 kilitli JSON SHA256 | ✅ **BUGÜN BİZZAT**: dosyaya bayt eklendi → `--task GS-01` → 0/1 KALDI (exit=1) → byte-aynı geri alma → SHA256 eşleşti → 1/1 GEÇTİ (exit=0) |
| GS-02 tüm .py derleme | ✅ **kanıtlandı 2026-09-09**: kökte bozuk `_denetim_mut.py` → KALDI (0/1) → dosya silindi → GEÇTİ (1/1). Proje ağacı 15 kirli dosyayla başlayıp 15 ile bitti, kalıntı yok. |
| GS-03 SpellingEngine yükleme | ✅ **kanıtlandı 2026-09-09**: `pipeline/product/rules_engine.py` geçici taşındı → KALDI (0/1) → geri alındı → GEÇTİ (1/1). Taşıma/geri alma olduğu için dosya byte-aynı; ağaç 15 → 15. |

## Özet karar önerileri (Han onayına)

1. ~~GV-01'i rglob'a çevir~~ **UYGULANDI 2026-09-09** (Han onayı).
   Kapsam 20 kök `.py` → 28 dosyaya çıktı; eklenen 8 dosya projenin ÇEKİRDEĞİ
   (`core/conformer.py`, `core/qa_gate.py`, `core/rasterizer.py`,
   `core/translator.py`, `core/arc_layout.py`, `core/presets.py`,
   `tools/augment_arc_engraved.py`, `tools/build_qa_proof_sheet.py`).
   `__pycache__` ve `.git` hariç tutuldu; dosya bulunamazsa exit=2 (sessiz
   geçiş engeli) eklendi.
   **Kanıt:** `core/conformer.py`'ye sözdizimi hatası enjekte edildi → GV-01
   **KALDI** (0/1) → byte-aynı geri alma → GEÇTİ (1/1). Eski `glob` sürümü bu
   hatayı göremezdi. Ağaç 0 → 0.
   **Karşılaştırılabilirlik notu (AGENT_EVAL_SPEC k.ç. 4):** GV-01 yerinde
   değiştirildi, yeni ID açılmadı. Bu tarihten ÖNCEKİ "GV-01 geçti" kayıtları
   yalnızca kök dizinin derlendiğini gösterir; alt dizinler hakkında bilgi
   vermez. Sonraki kayıtlar daha geniş bir kontrolü ifade eder.
2. ~~GS-02/GS-03 mutasyon kanıtları~~ **TAMAMLANDI 2026-09-09** (bkz. 3. bölüm).
   Kalan tek kanıt borcu: GV-01 (gokturk-vision kök .py derleme) için doğrudan
   mutasyon koşumu, ve GVER-01'in kendi kopyası (E:\gokturk_verify) üzerinde
   doğrudan koşum — bugün yalnız eşdeğerlik yoluyla kanıtlandı.
3. Her eval setinin yanına `kaldi-kanitlar.md` alışkanlığı: hangi görev hangi
   mutasyonla kanıtlandı, tarih + çıktı. (Bu raporun 3. bölümü ilk örnek.)

— Denetim sonu. Hiçbir görev dosyası bu denetim sırasında değiştirilmedi;
yalnızca GS-01 mutasyonu geçici uygulandı ve byte-aynı geri alındı.
