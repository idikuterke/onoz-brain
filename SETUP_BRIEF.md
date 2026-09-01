# Kurulum brifingi — onoz-brain

> Bu dosya, kurulumu yapacak **kodlama ajanına** verilir. Tek oturumda bitmeli.
> Ajan bu brifingi baştan sona okumadan hiçbir komut çalıştırmaz.

## Sen kimsin, ne yapıyorsun

`onoz-brain` adlı beceri kayıt ve yetki sistemini kullanıcının makinesine kuruyorsun.
Sistem, birden fazla projeye ortak beceri kütüphanesi servis eder ve her kullanımın
sicilini tutar. Sen bu sistemi **kuruyorsun**, kullanmıyorsun.

## Mutlak sınırlar

1. **Hiçbir proje dosyasını değiştirme.** Projelere yazacağın tek dosya `.brain.json`,
   onu da `brain.py link` komutu yazar. Kod, config, asset — hiçbirine dokunma.
2. **`brain.py`'yi değiştirme.** Hata bulursan raporla, düzeltme.
3. **Test yazmadan beceri ekleme.** `test.py` boş bırakılmış beceri kabul edilmez.
4. **Eval görevlerinin `verify` komutunu "geçsin diye" gevşetme.** Görev kalıyorsa
   sebebini raporla. Eşiği düşürmek ölçüm aletini bozmaktır.
5. **Sahte veri üretme.** `brain log` ile örnek/deneme kaydı yazma. Sicil sadece
   gerçek koşulardan doğar; kirletirsen tüm terfi mantığı çöker.

## Adımlar

### 1. Kurulum

```bash
git clone <repo-url> ~/onoz-brain
cd ~/onoz-brain
python brain.py init
```

`BRAIN_HOME` ortam değişkenini kalıcı ayarla (Windows: `setx BRAIN_HOME "%USERPROFILE%\onoz-brain"`).
`python brain.py list` çalışıyorsa kurulum tamam.

### 2. Projeleri bağla

`skills/CATALOG.md` içindeki tabloyu kullan. **Yolları kullanıcıdan iste, tahmin etme.**
Var olmayan dizin verilirse komut zaten hata verir — hatayı gizleme, kullanıcıya sor.

```bash
brain link <ad> <yol> --type <godot|flutter|web|python-tool> --tag <etiket>
```

Doğrulama: `brain link` sonrası her projede `.brain.json` olmalı ve
`brain list --project <ad>` beceri listesi dönmeli.

### 3. P0 becerilerini kur (8 adet)

`skills/CATALOG.md` içinde **P0** işaretli olanlar. Her biri için:

```bash
brain new "<beceri adi>" --applies-to <tip> --tag <etiket>
```

Sonra üç dosyayı da doldur:
- `SKILL.md` — "Ne zaman kullanılır" tek paragraf; "Kullanılmaz" **en az 2 madde**;
  "Sessiz hata riski" dürüstçe yazılmış.
- `test.py` — geçti/kaldı döndüren gerçek kod. Şablondaki `return 1` kalırsa iş bitmemiştir.
- `skill.json` — `verify` alanı gerçek komut.

P0 becerileri mevcut komutların sarmalayıcısıdır (`flutter test`, `npm run build`,
`pytest -q`). Yeni bir şey icat etme; var olanı doğrulanabilir hale getir.

### 4. Eval setini kalibre et

```bash
brain eval kutun-arinisi --dry-run
```

`[DUZELTME GEREKIR]` işaretli görevlerde sahne yolları, test scripti adları ve export
preset ismi **kullanıcının gerçek dosya yapısına** göre düzeltilecek. Yolları
tahmin etme, projede ara veya kullanıcıya sor.

Sonra baseline'ı al:

```bash
brain eval kutun-arinisi --record
```

Bu ilk sayı referans noktasıdır. **Düşük çıkması normaldir ve iyidir** — yükseltilecek
şey odur. Yüksek çıkarmak için görev gevşetmek en ağır kural ihlalidir.

### 5. Git

```bash
git add -A && git commit -m "chore: brain sistemi kuruldu, P0 becerileri ve KA eval baseline"
git push
```

`memory/runs/*.jsonl` ve `memory/evals/*.json` **commit edilir** — sicil repodadır.

## Kabul kriterleri

Aşağıdakilerin hepsi doğruysa iş bitmiştir:

- [ ] `brain list` hatasız çalışıyor, en az 9 beceri listeleniyor
- [ ] Bağlanan her projede `.brain.json` var
- [ ] `brain context <proje>` her proje için markdown brifing basıyor
- [ ] Her P0 becerisinde `test.py` şablon halinde değil, gerçek doğrulama yapıyor
- [ ] Hiçbir `SKILL.md`'de "Kullanılmaz" bölümü boş değil
- [ ] `brain eval kutun-arinisi --record` çalıştı, baseline `memory/evals/` altında
- [ ] `brain stats` çalışıyor ve **0 koşu** gösteriyor (sahte veri yok)
- [ ] Hiçbir proje dosyası değişmedi — `git status` her projede temiz

## Bitirince raporla

1. Bağlanan projeler ve tipleri
2. Kurulan P0 becerileri; hangilerinin `test.py`'si gerçekten çalıştırılıp doğrulandı
3. **Eval baseline: X/10**
4. Düzeltilemeyen `needs_adjust` görevleri ve sebebi
5. `brain.py`'de fark ettiğin ama düzeltmediğin hatalar
