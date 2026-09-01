# commit-mesaji-uret

> Beceri kimliği: `commit-mesaji-uret` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Commit açılmadan önce önerilen mesajın conventional commit biçimine
(`tip(scope)!: açıklama`; tip: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)
uyduğunu makineyle doğrulamak için; ajan kendi ürettiği mesajı bu filtreden geçirmeden
"hazır" dememelidir, geçersizse düzeltip yeniden sormalıdır.

## Kullanılmaz

- Commit'i oluşturmak veya koşmak için — bu beceri mesajı üretir/doğrular, git çalıştırmaz.
- Geçmiş commit'leri topluca denetlemek için — tek mesaj doğrular (--message/--message-file);
  git log taraması yapmaz.
- "Mesaj güzel mi" yargısı için — sadece biçim kontrolü yapar, içeriğin işi doğru anlatıp
  anlatmadığına bakmaz.

## Nasıl çalışır

1. `--message "fix(engine): ..."` ile tek mesaj, `--message-file` ile dosyadaki ilk satır verilir.
2. Regex eşleşir: tip küçük harf ve listede, scope (varsa) `[a-z0-9._/-]` karakterleri, `!` (varsa)
   kırıcı değişiklik işareti, `: ` ayracından sonra boş olmayan açıklama.
3. `--selftest` dahili geçerli/geçersiz örneklerle regex'in kendisini doğrular.

## Doğrulama

```
python test.py --selftest
```

Beklenen: çıkış kodu 0. Tek mesaj için: `python test.py --message "feat: ..."` → 0.

## Sessiz hata riski

Var. Regex yüzeyseldir: `fix: x` biçimce geçerlidir ama "x" hiçbir şey anlatmaz — bu beceri
mesajın işi doğru özetlediğini garantilemez, sadece biçimi. Ayrıca bilinçli katılıklar vardır:
tip yalnızca küçük harf kabul eder, `Merge branch ...` gibi git'in otomatik mesajları reddedilir
(kural, hata değil) ve açıklamada `: ` sonrası boşluk şartı vardır; bu kuralları bilmeyen biri
geçerli mesajı "reddedildi" sanabilir.
