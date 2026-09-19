# kos — beceriyi koştur ve sicile yaz, tek komutta

> Beceri kimliği: `kos` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Bir projede gerçek bir değişikliği doğrularken, `flutter test` / `npm run build` /
`godot --headless ...` yazmak yerine:

```
kos flutter-test-kos
```

Projeyi `.brain.json`'dan bulur, becerinin `verify` komutunu **gerçekten koşturur**,
sonucu çıkış kodundan alır, tek soru sorar (inceleme dakikası + müdahale) ve
`brain log`'u senin yerine çağırır. Sicil böyle dolar: iş günü koşularıyla,
ölçüm günü ritüelleriyle değil.

Neden var: `brain log` doğru şeyi istiyor ama yanlış anda istiyor — dört alan,
elle, iş bittikten sonra. On günde 135 commit atılıp sıfır log yazılması bunun
kanıtıydı.

## Kullanılmaz

- **Eval veya trial koşularını sicile sokmak için.** Kırmızı çizgi 3: deneme
  kaydı `brain log` ile yazılmaz. `brain eval` / `brain trial` kendi kayıtlarını
  `memory/evals/` altına yazar; `kos` yalnız gerçek geliştirme kapıları içindir.
- **Sırf sayaç için.** Aynı commit için analyze + test'i iki koşu diye yazmak,
  ya da "acaba geçiyor mu" merakıyla koşturup loglamak sicili şişirir. Bir
  doğrulama kapısı = bir koşu.
- **Geçmişe dönük.** Dün koşulan bir testi bugün `kos` ile "yeniden koşup"
  loglamak, koşuyu bugüne tarihler. Kayıt anında yazılır.
- **Araç PATH'te değilken.** `kos` bunu ayırt eder (`KOSAMADI`, exit 2, sicile
  yazmaz) ama sen bunu "kaldı" diye okuma — ortam sorunu, kapı sonucu değil.
- Kendi test'ini ölçmek için (`kos kos` anlamsızdır).

## Nasıl çalışır

1. cwd'den yukarı `.brain.json` arar → proje adı ve kökü.
2. `$BRAIN_HOME/skills/<beceri>/skill.json` → `verify`. `python test.py ...`
   biçimi beceri dizinine çözülür (`--project .` gibi ekler korunur); diğer
   komutlar proje kökünde olduğu gibi koşar.
3. Koşturur, süreyi ölçer. `exit 0 → pass`, aksi `→ fail`. Komut bulunamadıysa
   (exit 127/9009 veya "not recognized") → `KOSAMADI`, exit 2, **log yok**.
4. `--review-min` ve `--autonomous/--assisted` verilmediyse sorar.
5. `python brain.py log --project P --skill S --result R --review-min N [--autonomous] --note ...`

`brain.py`'ye dokunmaz — Özellik Dondurma korunur; `anonim-export` gibi
bağımsız betik.

## Doğrulama

```
python test.py
```

Beklenen: çıkış kodu 0. Test **hermetiktir**: geçici `BRAIN_HOME`, sahte
`brain.py` ve geçici proje kurar; gerçek sicile dokunmaz. Beş davranışı
doğrular: alt dizinden proje bulma, geçen/kalan verify, `--dry-run`'ın
yazmaması, `KOSAMADI`'nın exit 2 dönüp yazmaması, `brain log`'un doğru
argümanlarla çağrılması.

## Sessiz hata riski

Var, iki yönde. (1) `kosamadi()` sezgisel: stderr'de "not found" benzeri iz
arar. Kapı gerçekten kaldığı halde çıktıda o kelimeler geçerse (örn. bir
testin kendi mesajı "file not found" diyorsa) koşu yanlışlıkla `KOSAMADI`
sayılıp **loglanmaz** — kaybolan bir başarısızlık kaydı. (2) Tersi: araç var
ama yanlış sürüm çalışıyorsa exit 0 döner, `pass` loglanır, kapı aslında
doğru şeyi ölçmemiştir. İkisi de `kos`'un değil `verify`'ın dürüstlüğüne
bağlı; `kos` yalnız taşır.
