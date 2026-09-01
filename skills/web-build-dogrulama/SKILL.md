# Web build doğrulama

> Beceri kimliği: `web-build-dogrulama` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Bir web projesinde (package.json'lı: Next.js, statik site, oyun...) production build'in
(`npm run build`) kırılmadığını doğrulamak için; deploy/dit öncesi zorunlu geçiş kapısı ve
repo-sanity-check zincirinin web ayağının çekirdek adımıdır.

## Kullanılmaz

- Geliştirme sunucusu / runtime duman testi için — build başarısı `next start`'ın hatasız
  çalıştığını garanti etmez; runtime hataları build'i geçebilir.
- Lint/test ayrıştırması için — package.json'da `lint`/`test` script'i varsa zincirleme koşu
  `repo-sanity-check`'in işidir.
- `build` script'i tanımlı olmayan projede — exit 2 döner; script uydurulmaz.

## Nasıl çalışır

1. `npm` PATH'te aranır (`--npm` ile yol verilir; Windows'ta `npm.CMD` bulunur) — yoksa 2.
2. `package.json` okunur; `scripts.build` tanımlı mı bakılır — yok/bozuksa 2.
3. `npm run build` proje dizininde (cwd) koşulur; çıkış kodu 0 → geçti, 0 dışı →
   çıktının son 25 satırı basılıp KALDI.

## Doğrulama

```
python test.py --project <web-proje-yolu>
```

Beklenen: çıkış kodu 0.

## Sessiz hata riski

Var. (1) Build "başarılı" ama içerik eksik olabilir: build'e girmeyen bir sayfa/rota, yanlış
export ayarı veya boş `dist/`/`.next/` çıktısı bu testin exit kodunu değiştirmez — çıktı
dizininin dolu olduğunu gözle doğrulamak hâlâ insan işidir (bkz. bundle-boyut-esigi, P2).
(2) `node_modules` kurulu değilse npm, "command not found" benzeri bir hata ile 1'den döner;
bu semantik olarak ön koşul eksikliği olsa da 1 (KALDI) görünür — npm'in hata kodları sürüme
göre değiştiği için güvenilir ayrım yapılamaz; çıktıya bakıp `npm install` koşulmalıdır.
