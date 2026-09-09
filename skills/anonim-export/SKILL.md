# Anonim export

> Beceri kimliği: `anonim-export` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

onoz-brain sicilini (memory/runs + memory/evals + memory/lessons) dış dünyaya
paylaşılabilir açık-veri paketine çevirmek için: aylık dataset üretiminde,
README "Evidence" bölümü beslemede ve case study yazarken ham kayıt gerekdiğinde.
Proje adlarını SHA1 tabanlı kararlı takma adlara çevirir (aynı proje her
export'ta aynı kodu alır), yerel yolları ve e-postaları çıktıdan kırpar.

## Kullanılmaz

- Sicile kayıt yazmak için — bu beceri salt-okur çalışır, hiçbir koşu üretmez;
  kayıt yazma işi `brain.py`'ye aittir ("sahte sicil yok" kuralı).
- brain.py motorunu değiştirmek veya özellik eklemek için — bu beceri motordan
  bağımsız bir dış araçtır; Özellik Dondurma kuralı (10 koşu bariyeri) burayı
  etkilemez ama motor dosyasına da dokunulmaz.
- Gerçek adlarla paylaşım için — `--real-names` bayrağı kimlik açar; çıktısı
  asla public klasöre/reponya kopyalanmaz.

## Nasıl çalışır

1. `BRAIN_HOME` (veya `--brain-home`) altındaki `projects.json` ve `memory/`
   okunur. Kaynaklara yazma işlemi yapılmaz.
2. Takma ad tablosu üretilir; runs/evals/lessons kayıtları proje koduyla
   yeniden yazılır; not alanları yol/e-posta temizliğinden geçirilir.
3. Çıktı klasörüne `runs.jsonl`, `evals.jsonl`, `lessons.json`, `summary.csv`,
   `summary.json`, `README.md` yazılır. Zaman damgası "şimdi" değil, verideki
   en büyük ts'den (`as_of`) türetilir — aynı veri, bit-bit aynı çıktı.

```
python scripts/brain_export.py --out ./out/brain-dataset-2026-09
```

## Doğrulama

```
python test.py
```

Beklenen: çıkış kodu 0. Test sahte bir brain-home kurar; gizlilik temizliğini,
çıktı determinizmini (iki kosuda SHA256 eşitliği) ve takma ad kararlılığını
doğrular. Gerçek sicile dokunmaz.

## Sessiz hata riski

Var. (1) Bu beceri not alanlarını mekanik olarak temizler ama **isim** temizlemez:
sicil notuna yazılmış gerçek kişilik ad ("Han", okul, müşteri) export'a olduğu
gibi geçer — anonimleştirmenin birinci hattı yazım anındaki disiplindir, bu
betik yalnızca ikinci savunma hattıdır. (2) `--real-names` ile üretilen çıktı
testten geçer ve "temiz" görünür; paylaşım öncesi çıktı klasöründe
`real-names.txt` diye bir işaret dosyası yoksa varsayım "takma adlı"dır — bayrak
kullanıldıysa çıktıyı hemen yeniden adlandırın. (3) Kaynak sicildeki zayıf
`note` verisi export'un değerini sınırlar: betik veriyi zenginleştirmez,
yalnızca taşır — "az kayıt" görünümü verinin gerçek halidir, kozmetik doldurma
yapılmaz.
