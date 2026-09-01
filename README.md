# onoz-brain

Tek merkezde duran beceri kütüphanesi. 10+ projeye servis eder, her kullanımın sicilini tutar, becerileri **kanıta dayalı** olarak terfi ettirir.

Bağımlılık yok — Python 3.9+ standart kütüphane. Model bağımsız: hangi ajanı kullandığın sistemin umurunda değil.

---

## Kurulum

```bash
git clone <repo-url> ~/onoz-brain
cd ~/onoz-brain
python brain.py init
```

`BRAIN_HOME` ortam değişkeni ile başka yere de koyabilirsin (varsayılan `~/onoz-brain`).

Windows PowerShell kalıcı ayar:
```powershell
setx BRAIN_HOME "C:\Users\<sen>\onoz-brain"
```

Kısayol (bash):
```bash
alias brain="python $BRAIN_HOME/brain.py"
```

---

## Projeleri bağla

Sistem projelerin **içine hiçbir şey kopyalamaz**. Sadece `.brain.json` adında bir işaret dosyası bırakır. Symlink yok — Windows ve Linux'ta aynı davranır, projeyi taşırsan bozulmaz.

```bash
brain link kutun-arinisi ~/projects/kutun-arinisi --type godot --tag gdscript
brain link onoz-idle     ~/projects/onoz-idle     --type godot --tag idle
brain link gokyazi       ~/projects/gokyazi       --type flutter --tag dart
brain link onoz-web      ~/projects/onoz-web      --type web --tag nextjs
```

Bir beceri hangi projelerde görünecek? `skill.json` içindeki `applies_to` belirler. Boş bırakırsan **her projede** görünür.

---

## Günlük döngü

```bash
# 1. Ajana brifing ver — hangi araca çalıştığın fark etmez
brain context kutun-arinisi > /tmp/brief.md
#    (veya doğrudan boru: brain context kutun-arinisi | your-agent)

# 2. Ajan çalışır, sen doğrularsın

# 3. Sonucu kaydet — SİSTEMİN TEK BESLENME NOKTASI BURASI
brain log --project kutun-arinisi --skill godot-scene-smoke-test \
          --result pass --autonomous --review-min 4

# 4. Başarısızlıktan kural çıkar
brain lesson --skill godot-scene-smoke-test \
             --rule "Autoload sahneleri --quit-after 2 ile erken kapanıyor, 4 kullan"

# 5. Haftalık: nerede duruyoruz
brain stats
brain promote            # salt okunur, adayları gösterir
brain promote --apply    # sen onaylayınca uygular
```

`log` adımını atlarsan sistem öğrenmez. Tek disiplin gereksinimi bu.

---

## Yetki merdiveni (sistemin anayasası)

| Seviye | Sistem ne yapar | Sen ne yaparsın | Terfi koşulu |
|---|---|---|---|
| **L0** | Önerir | Uygularsın | 10 koşu, ≥%80 kabul |
| **L1** | Uygular, branch açar | Merge edersin | 20 koşu, ≥%90 başarı |
| **L2** | Test geçerse otomatik merge | Haftalık denetim | 50 koşu, ≥%95, 0 sessiz hata |
| **L3** | Kendi görevini üretir | Aylık denetim | — |

**Terfi otomatik değildir.** `promote` sadece hesaplar; `--apply` senin onayındır.

**Sessiz hata** (test geçti ama sonuç yanlış) her şeyi keser: son 20 koşuda bir tane varsa beceri bir seviye **düşürülür**. Bu tek kural, sistemin şişip güvenilmez hale gelmesini engelleyen şeydir.

---

## Beceri kabul sözleşmesi

Yeni beceri:

```bash
brain new "godot asset import dogrulama" --applies-to godot --tag asset
```

Kütüphaneye kabul için üçü de zorunlu:

1. **`SKILL.md` doldurulmuş** — özellikle "Kullanılmaz" bölümü. Boşsa kabul yok.
2. **`test.py` yazılmış** — makinenin geçti/kaldı diyebileceği tek komut. Öznel kriter yasak.
3. **Yeni bir eval görevi** eklenmiş — yoksa büyümeyi ölçemezsin.

Testiyle gelmeyen beceri kütüphaneye girmez. Bu kural esnetilirse sistem 6 ay içinde çöp yığınına döner.

60 gün çağrılmayan beceri `brain list` çıktısında `[BAYAT]` işaretlenir → arşive aday.

---

## Ölçtüğümüz şey

`brain stats` üç sayı verir. Önem sırası:

1. **Otonomi oranı** — müdahalesiz tamamlanan koşu yüzdesi. Yükselmeli.
2. **Görev başına inceleme dakikan** — asıl darboğaz bu. Düşmeli.
3. **Sessiz hata** — sıfır olmalı. Değilse terfi durur.

İnceleme dakikan düşmüyorsa sistem büyümüyor, sadece şişiyor.

---

## Döngüye asla girmeyecekler

Kalıcı L0, terfi edilemez: mimari kararlar, lore/kanon tutarlılığı, yayın kararı, lisans/IP, para.

Otomasyon kazancı küçük, hata maliyeti geri alınamaz.

---

## Dizin yapısı

```
onoz-brain/
├── brain.py                 # tek dosya CLI, bağımlılıksız
├── projects.json            # bağlı projeler (üretilir)
├── skills/
│   ├── _template/           # yeni beceri kalıbı
│   └── <beceri-adı>/
│       ├── SKILL.md         # sözleşme: ne zaman / kullanılmaz / doğrulama
│       ├── skill.json       # seviye, applies_to, etiketler
│       └── test.py          # geçti/kaldı
├── evals/                   # proje bazlı görev setleri
└── memory/
    ├── runs/YYYY-MM.jsonl   # sicil — commit EDİLİR, git'te diff'lenir
    └── lessons/             # hatalardan çıkan kurallar
```

Koşu kayıtları JSONL ve commit edilir: sicilin kendisi repoda, geçmişi git'te görünür. Otonomi grafiğini bu dosyalardan üretirsin.
