# Brif — career-ops'a kanıt köprüsü (cv-facts.json + profile.yml)

> Hazırlandı: 2026-09-20. `C:\Users\pc\Documents\antigravity\intelligent-newton`
> dizininde çalışan ajana verilecek. Bu depo `santifer/career-ops`'un fork'udur;
> kullanıcı burada başvuru hattını işletiyor (16 başvuru, `data/applications.md`).

## Sorun

Üretilen CV'lerde neyin iddia edilebileceğini sınırlayan `config/cv-facts.json`
**boş** (yalnız `.example` var). Hat şu an kanıt kapısı olmadan CV üretiyor.
Somut belirti: `data/applications.md` #005 ve #014'te "Tunga 178 Headless Test"
geçiyor; gerçek sayı **192** (ölçüm 2026-09-09) ve bunu yakalayacak bir şey yok.

Ayrıca `config/profile.yml`'in kanonik kopyası artık başka bir depoda
(`C:\Users\pc\kariyer\meta-cv\profile.yml`). İki kopya sessizce ayrışacak.

## Kanıt kaynağı — DOKUNMA, yalnız oku

```
C:\Users\pc\kariyer\meta-cv\yetkinlikler.yml
```

Şema (YAML):

```yaml
yetkinlikler:
  - ad: "..."                    # Türkçe başlık
    teknik_ad: "..."             # İngilizce teknik ad
    seviye: kanitli              # kanitli | uygulanmis | ogreniliyor
    kanit:                       # proje / commit / eval / olcum — hangisi varsa
      proje: onoz-brain
      commit: ["014fb9f", "..."]
      olcum: "3/3 soğuk ölçüm GEÇTİ"
    aciklama: >  ...             # Türkçe
    cv_cumlesi: >  ...           # İngilizce, CV'ye girecek cümle
    roller: [generative-pipeline-ta, ...]
```

Kural: bu dosya **tek kaynak**. Buraya yazma; eksik görürsen raporla.
Kanıtı olmayan iddia orada yok — o yüzden orada olmayan şey CV'ye de girmez.

## İş 1 — `cv-facts.json`'u `yetkinlikler.yml`'den ÜRET

Önce doğrula: career-ops `cv-facts.json`'u gerçekten okuyor mu?
`cv-sync-check.mjs`, `cv-sections-core.mjs`, `build-cv-*.mjs` içinde
`cv-facts` / `allow_facts` / `forbidden_phrases` ara. **Okumuyorsa köprü
kurma, raporla** — boşa altyapı yazma.

Okuyorsa, `scripts/` altına (ya da deponun kendi konvansiyonuna uygun yere)
küçük bir üretici yaz: `yetkinlikler.yml` → `config/cv-facts.json`.

| `cv-facts.json` alanı | Nereden |
|---|---|
| `allow_facts` | her kaydın `cv_cumlesi` (yalnız `seviye: kanitli` olanlar) |
| `allow_metrics` | `kanit.olcum` ve `aciklama` içindeki kanıtlı sayılar: `192`, `3/3`, `10/10`, `164`, `172` … |
| `forbidden_phrases` | bilinen bayat sayılar: `"178"` (Tunga test sayısı, artık 192); `seviye: ogreniliyor` olan her kaydın iddiası |
| `warn_phrases` | `seviye: uygulanmis` kayıtlar (kanıt var ama otomatik ölçüm yok) |

Üretici **idempotent** olsun: iki kez koşunca aynı dosya çıksın. Elle
düzenleme yasağını dosyanın başına yorum olarak yaz
(`// URETILDI: kariyer/meta-cv/yetkinlikler.yml'den — elle duzenleme`).

## İş 2 — `config/profile.yml`'i kopya olmaktan çıkar

Hedef: `config/profile.yml` ile `C:\Users\pc\kariyer\meta-cv\profile.yml`
**tek dosya** olsun.

Sırayla dene:

1. `mklink config\profile.yml C:\Users\pc\kariyer\meta-cv\profile.yml`
   (sembolik bağ; Windows'ta yönetici ya da Geliştirici Modu ister)
2. Olmazsa `mklink /H ...` (hard link; aynı sürücüde olmalı — burada C: / C:, olur)
3. O da olmazsa: bağ kurma, `scripts/` altına tek yönlü senkron betiği yaz
   (`kariyer → career-ops`, asla tersi) ve bunu İş 1'deki üreticiye bağla.

Önce mevcut iki dosyayı `diff` et. Fark varsa **kariyer'deki kazanır**
(orası kanonik); career-ops'taki farkı raporla, sessizce ezme.

`DATA_CONTRACT.md`'yi oku: `profile.yml` "User Layer — NEVER auto-updated"
katmanında. Bağ kurmak bunu ihlal etmez; upstream güncellemesi o dosyaya
dokunmaz.

## Kırmızı çizgiler

1. `yetkinlikler.yml`'e yazma. Kanonik ve başka depoya ait.
2. `config/` dışında career-ops'un **System Layer** dosyalarına dokunma
   (`DATA_CONTRACT.md` hangilerinin olduğunu söylüyor).
3. `data/applications.md`'deki geçmiş satırları değiştirme — "178" oradaki
   başvurularda **doğruydu**, o gün öyle gönderildi. Kapı gelecekteki CV'ler için.
4. Kanıtsız hiçbir cümleyi `allow_facts`'e ekleme, "iyi durur" diye.
5. Commit ederken pathspec kullan (`git commit -- <dosya>`); depo 4 kirli
   dosyayla başlıyor, onları içine alma.

## Teslim

1. Üretici betik + üretilmiş `config/cv-facts.json`
2. `config/profile.yml` bağ (veya senkron betiği) + hangi yöntemin işlediği
3. Doğrulama çıktısı (aşağıda)
4. Kısa rapor: career-ops `cv-facts.json`'u nerede/nasıl okuyor; `profile.yml`
   diff'inde ne çıktı

## Doğrulama — bunlar geçmeden bitmiş sayılmaz

```
node <uretici>            # iki kez koş, ikinci koşuda diff bos olmali
grep -c '"178"' config/cv-facts.json         # >= 1 (forbidden'da)
grep -c '192' config/cv-facts.json           # >= 1 (allow_metrics'te)
node cv-sync-check.mjs                       # varsa; 178 iceren bir CV'yi reddetmeli
diff config/profile.yml C:\Users\pc\kariyer\meta-cv\profile.yml   # bos
git status --porcelain                       # yalniz senin dosyalarin
```

Son test: `allow_facts` içinden bir cümleyi geçici olarak silip CV üretimini
koş — o cümle CV'de çıkmamalı. Çıkıyorsa kapı çalışmıyor demektir; geri al ve
raporla.
