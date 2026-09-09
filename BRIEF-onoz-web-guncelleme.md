# Brif — onozlabs sitesini güncelle (özgeçmiş + proje durumları)

> Hazırlandı: 2026-09-09. `C:\Users\pc\onozlabs` dizininde açılacak bir oturuma
> verilmek üzere. Oturuma başlarken ilk iş: `brain context onoz-web`.

## Amaç

Sitede yayınlanan özgeçmiş ve proje bilgileri bayatladı. İki kaynak var ve
ikisi de artık kanıtlı:

| Kaynak | Ne verir |
|---|---|
| `C:\Users\pc\kariyer\meta-cv\yetkinlikler.yml` | 10 yetkinlik kaydı, her biri commit/eval kanıtlı |
| `C:\Users\pc\kariyer\meta-cv\profile.yml` | kimlik, hedef roller, anlatı, proof_points |

**Kural:** Siteye giren her cümlenin `yetkinlikler.yml`'de kaydı olmalı. Kaydı
yoksa siteye de girmez. Kanıtsız iddia yazma.

Not: `yetkinlikler.yml`'deki `cv_cumlesi` alanı **İngilizce** (başvuru paketi
için). Site Türkçe — `aciklama` alanını kullan, `cv_cumlesi`'ni çevirme.

## Kapsam

### 1. `app/(site)/ozgecmis/page.tsx` (400 satır)

Üç bölüm var: *Geliştirilen Sistemler & Ürünler*, *Deneyim & Kurumsal Liderlik*,
*Eğitim & Yetkinlikler*.

Eklenecek/güncellenecek olan, 2026-09-09'da kanıtlanan işler:

- **Ajan değerlendirme altyapısı (onoz-brain)** — sitede hiç yok. 13 bağlı
  proje, soğuk otonomi ölçümü (3/3), ölçüm aletinin kendisinin denetlenmesi.
- **Ölçülmüş test sayısı düzeltmesi** — Kut'un Arınışı için sitede eski bir
  sayı geçiyorsa **192** olmalı (ölçüm 2026-09-09; profile.yml'de düzeltildi,
  eskiden 178 yazıyordu). Sitede geçen her sayıyı `yetkinlikler.yml` ile
  karşılaştır.
- **Yetkinlikler bölümü** — `Evaluation & Reproducibility` sınıfı eklendi:
  soğuk başlangıçlı ajan değerlendirmesi, mutasyonla kanıtlanan kontroller,
  çalıştırılabilir mimari karar kayıtları.

### 2. `data/apps.ts` — proje durumları

Şu an beş uygulama var (`gokyazi` yayinda, `gokyuzu-gunlugu` yakinda,
`gokturkce-yapayzeka-studio` beta, `onoz-idle` yayinda, +1).

**`durum` alanlarını kanıtla doğrula.** Örnek: `gokyuzu-gunlugu` "yakinda"
görünüyor ama proje aktif ve 164 testi geçiyor (eval `GG-01..03`, 3/3). Durum
gerçekten "yakinda" mı, karar kullanıcınındır — **sen tespit et ve sor**,
kendiliğinden değiştirme.

`ozellikler` listeleri de bayat olabilir; `kariyer/meta-cv/profile.yml`
içindeki `proof_points` ile karşılaştır.

## Kısıtlar — CONVENTIONS.md'yi oku, en kritik olanlar

**Site statik export.** `next.config.mjs` içinde `output: 'export'`. Sunucu
tarafı çalışma zamanı **yok**: API route, Server Action, middleware, ISR,
dinamik `cookies()` kullanılamaz. Build hatası ararken ilk buraya bak.

**İçerik `data/` altında yaşar.** Sayfayı değil veriyi düzenle; sayfa
bileşenleri oradan okur.

**`eslint --fix` bu projede güvenli değil.** `app/layout.tsx` içindeki
`eslint-disable-next-line` yorumlarını `{ }` gibi anlamsız bir ifadeye çevirip
bastırma direktiflerini siler. `--fix` koştuysan diff'i **mutlaka oku**.

**17 lint hatası bilinçli açık.** Hepsi `components/Scene3D/` ve
`components/melibo/` içinde React Compiler saflık kuralları. Mekanik değil;
bileşenin niyeti anlaşılmadan düzeltilirse render döngüsü bozulur. **Bu
bölgelere dokunma** — görev özgeçmiş ve veri katmanı.

**JSX metninde düz tırnak yasak.** `&quot;` / `&apos;` yaz;
`react/no-unescaped-entities` hata verir. Attribute tırnaklarına dokunma.

## Teslim edilecekler

1. Güncellenmiş `app/(site)/ozgecmis/page.tsx`
2. Güncellenmiş `data/apps.ts` (yalnız kanıtla doğrulanan alanlar)
3. `npm run build` başarılı
4. `npm run lint` hata sayısı **17'yi geçmiyor** (yeni hata ekleme)
5. Ağaç temiz bırakılmış: `git status --porcelain` boş

## Kırmızı çizgiler

1. Kanıtsız cümle yazma. `yetkinlikler.yml`'de kaydı yoksa siteye girmez.
2. Sayıları uydurma. Sitede geçen her rakam kanıt dosyasıyla eşleşmeli.
3. `Scene3D` ve `melibo` bileşenlerine dokunma.
4. `eslint.config.mjs`'e kural devre dışı bırakma ekleme; gerekiyorsa
   kullanıldığı yerde `// eslint-disable-next-line` + gerekçe.
5. `durum` alanlarını kendiliğinden değiştirme — tespit et, sor.
6. Commit ederken **pathspec kullan** (`git commit -- <dosya>`); düz
   `git commit` index'te bekleyen başka işi de içine alır.

## Kabul kontrolü (kullanıcı)

```
npm run build                      # basarili olmali
npm run lint                       # hata <= 17
git status --porcelain             # bos
grep -c "192" app/(site)/ozgecmis/page.tsx    # eski sayi kalmis mi
```

Ve her yeni cümle için tek soru: **"bunun kanıtı `yetkinlikler.yml`'de hangi
kayıt?"** Cevap yoksa cümle geri çevrilir.

## Dağıtım

Site Vercel'de `onozlabs` projesine bağlı; `main`'e push otomatik deploy
tetikler. Doğrulama:

```
npx vercel inspect onozlabs.com
curl -sSL --ssl-no-revoke -o /dev/null -w "%{http_code}\n" https://onozlabs.com
```

`--ssl-no-revoke` olmadan Windows'ta sertifika iptal denetimi başarısız olup
**site çökmüş gibi `HTTP 000`** döndürür — buna aldanma.
