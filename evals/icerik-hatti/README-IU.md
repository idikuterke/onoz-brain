# icerik-hatti — IU eval seti (bulut oturumundan birlestirildi)

**Proje tipi:** python (deterministik uretim hatlari koleksiyonu)
**Depo:** idikuterke/icerik-uretim-hatti — 11 hat, ortak cekirdek `core/` + `core_3d/`

## Neden GPU'suz

Hattin kendisi yereldir (ComfyUI 127.0.0.1:8188, Blender 4.5, RX 7700 XT/ROCm). Eval
seti **uretim kosmaz**; sozlesme/sema/kapi-kapsami denetler. Hepsi saf Python, GPU'suz,
Linux ve Windows'ta ayni. Boylece regression orani donanima bagli dalgalanmaz.

## Set (9 regression, bulut baseline 9/9; yerelde 8/9 — IU-04 gercek kapi hatalarini yakaliyor, 2026-10-08)

| id | ne koruyor |
|---|---|
| IU-01 | `core` + `core_3d` derlenir (syntax/sozluk) |
| IU-02 | her hattin `pipeline.json` gecerli ve `hat.ad` dizin adiyla ayni |
| IU-03 | `donergec-3d` zincirinin (`govde -> anim-paketle -> sahnele`) her adiminin kapisi var |
| IU-04 | `python -m core dogrula` ciktisinda `donergec-3d` bloğu SORUNSUZ |
| IU-05 | uslup sizmasi yok: `prompt_suffix` anahtarlari yalniz pipeline.json'un bilinen 4 yolunda |
| IU-06 | sahne spec'leri (`donergec-3d/sahneler/*.json`) gecerli |
| IU-07 | Trellis'i 3/3 asan `kagit_yigini` devre disi kalir |
| IU-08 | kararlilik korumalari import edilebilir (`gpu_kilit`, `gozetmen`, `gates`) |
| IU-09 | `donergec-teaser/configs/senaryo/bolum1.json` gecerli |

## Neden bu dokuz

Proje gunlugunden (`docs/DEVAM.md`) cikan gercek kayip bicimleri:

- **Kapi kapsami gerileme** (IU-03, IU-04): `donergec-3d` 11 hattin **tek** %100 kapi
  kapsamli hatti. Kapisiz adim = olcusuz uretim; AGENTS.md 7b esigi dusurmeyi yasakliyor.
  Bu iki gorev kapsamin sessizce dusmesini yakalar.
- **Uslup bulasmasi** (IU-05): mitolojik uslup Donergec'e bir kez karisti ve ayiklamak
  icin hat ikiye bolundu. Besinci bir `prompt_suffix` anahtari = yeni bulasma yolu.
- **Trellis asilmasi** (IU-07): 3 ayri kagit promptu asildi, gozetmen restart etti.
  `_devre_disi` isareti kalkarsa kuyruk gece yarisi asilir.
- **Sema cürümesi** (IU-02, IU-06, IU-09): 11 hat tek cekirdege yaziyor; bir hattin
  `hat.ad`'i dizinden kayarsa `core dogrula` yanlis hatti denetler.

## Kapsam disi (bilerek)

- **Uretim cikti kalitesi** — render/mesh kalitesi gozle ve `kontrol_*.py` ile olculur,
  eval'de degil. Kapilar zaten uretim aninda vuruluyor.
- **Kapisiz 10 hat** — `gokyazi-*`, `mitoloji-3d`, `godot-3d`, `onozidle-2d`.
  Bugunku dogru durum "kapisiz"; regression yapsam baseline %100 olmazdi.
  Kapi eklemek **ajan gorevi** adayidir, regression degil.
- **Ajan gorevi yok** — henuz. Ilk aday: `godot-3d` kapi eklemesi (0/2 -> 2/2).
