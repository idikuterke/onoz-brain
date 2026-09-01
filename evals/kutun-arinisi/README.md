# Kut'un Arınışı — eval seti

10 görev. Hepsi **otomatik doğrulanabilir**: makine geçti/kaldı diyebiliyor.

`needs_adjust: true` olanlar senin dosya yollarına göre düzeltilmeli (sahne yolu,
test scripti adı, export preset ismi). Bir kez düzelt, sonra sabit kalsın —
**eval seti değişirse geçmiş ölçümler karşılaştırılamaz hale gelir.**

## Bilerek dışarıda bırakılanlar

Bunlar ölçülemez, eval'e **girmeyecek**:

- "Dövüş hissi iyi mi", "zorluk dengeli mi" — öznel
- "Lore tutarlı mı" — kanon kararı, kalıcı L0
- "Asset güzel mi" — üretim var, öğrenme yok

Bu ayrım sistemin belkemiği. Ölçülemeyen şeyi eval'e koyarsan pass rate anlamını kaybeder.

## Kullanım

```bash
brain eval kutun-arinisi --dry-run    # ne calisacak, gor
brain eval kutun-arinisi              # calistir
brain eval kutun-arinisi --record     # sonucu memory/evals/ altina yaz
brain eval kutun-arinisi --task KA-04 # tek gorev
```

İlk çalıştırma **baseline**'dır. O sayıyı not al; ilerlemeni ona göre ölçeceksin.
