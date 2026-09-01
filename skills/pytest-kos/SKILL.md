# pytest koşu

> Beceri kimliği: `pytest-kos` · Seviye ve sicil `skill.json` + `brain.py list` üzerinden okunur.

## Ne zaman kullanılır

Bir `python-tool` projesinde test paketini `pytest -q` ile koşup geçti/kaldı kararı vermek
için; her değişiklik sonrası, commit öncesinde ve repo-sanity-check zincirinin python
ayağı olarak çalıştırılır.

## Kullanılmaz

- Lint/format için — o iş `ruff-lint`'in (P1); pytest yalnızca test koşar.
- Test dosyası ve pytest konfigürasyonu taşımayan projede — exit 2 döner; boş geçiş
  "geçti" sayılmaz.
- Yayın (publish) doğrulaması için — paketleme/dağıtım ayrı bir iştir.

## Nasıl çalışır

1. `pytest` PATH'te aranır; yoksa `--python` (varsayılan: bu yorumlayıcı) ile
   `python -m pytest -q` fallback'i kullanılır.
2. Projede `pyproject.toml`/`setup.py`/`setup.cfg`/`pytest.ini`/`tox.ini` veya test dosyası
   (`test_*.py` / `*_test.py` / `tests/`) aranır — hiçbiri yoksa ön koşul (2).
3. `pytest -q` proje dizininde (cwd) koşulur; exit 0 → geçti, exit 5 (test toplanamadı) →
   2, diğer → çıktının son 25 satırı basılıp KALDI.

## Doğrulama

```
python test.py --project <python-proje-yolu>
```

Beklenen: çıkış kodu 0.

## Sessiz hata riski

Var. (1) Assertion'sız testler (`def test_x(): pass`) çıkış kodu 0 üretir — bu beceri
test kalitesini veya coverage'ı ölçmez, sadece koşar. (2) PATH'te pytest yoksa fallback
farklı bir yorumlayıcı/ortamda koşabilir: `--python` projenin venv'iyle aynı değilse
site-packages farkı yüzünden testler yanlış sonuç verebilir; venv'li projede
`--python <venv>\Scripts\python.exe` ile sabitle. (3) `pytest -q` bazı eklenti
uyarılarını (deprecation) exit 0'da gizler; temiz çıktı "uyarı yok" demek değildir.
