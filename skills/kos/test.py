#!/usr/bin/env python3
"""kos becerisinin kendi testi. Hermetik: gecici bir BRAIN_HOME ve gecici bir
proje kurar, gercek sicile DOKUNMAZ. Alti davranisi dogrular:

  1. .brain.json'dan projeyi bulur (alt dizinden de)
  2. verify'i proje kokunde kosturur; exit 0 -> GECTI, exit 1 -> KALDI
  3. --dry-run sicile yazmaz
  4. komut bulunamazsa KOSAMADI der, exit 2 doner, sicile yazmaz
  5. program ciktisinda "File not found" gecen gercek KALDI, KOSAMADI sayilmaz
  6. (dry-run disi) brain log'u dogru argumanlarla cagirir
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
KOS = HERE / "kos.py"


def kur(tmp: Path, verify: str) -> tuple[Path, Path]:
    home = tmp / "home"
    (home / "skills" / "deneme").mkdir(parents=True)
    (home / "skills" / "deneme" / "skill.json").write_text(
        json.dumps({"id": "deneme", "level": "L0", "verify": verify}), encoding="utf-8")
    # sahte brain.py: log cagrisini bir dosyaya yazar
    (home / "brain.py").write_text(
        "import sys, pathlib\n"
        "pathlib.Path(__file__).with_name('LOG_CAGRISI').write_text(' '.join(sys.argv[1:]))\n"
        "print('Kayit alindi (sahte)')\n", encoding="utf-8")
    proje = tmp / "proje"
    (proje / "alt" / "dizin").mkdir(parents=True)
    (proje / ".brain.json").write_text(json.dumps({"project": "test-projesi", "type": "python-tool"}),
                                       encoding="utf-8")
    return home, proje


def kos(home: Path, cwd: Path, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, BRAIN_HOME=str(home))
    return subprocess.run([sys.executable, str(KOS), *args], cwd=str(cwd),
                          env=env, capture_output=True, text=True, errors="replace")


def main() -> int:
    hatalar = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        # 1+2+3: alt dizinden proje bulma, gecen verify, dry-run
        home, proje = kur(tmp, f'"{sys.executable}" -c "import sys; sys.exit(0)"')
        r = kos(home, proje / "alt" / "dizin", "deneme", "--dry-run")
        if r.returncode != 0 or "test-projesi" not in r.stdout or "GECTI" not in r.stdout:
            hatalar.append(f"gecen verify / alt dizin: exit={r.returncode}\n{r.stdout}{r.stderr}")
        if (home / "LOG_CAGRISI").exists():
            hatalar.append("--dry-run sicile yazdi!")

        # 2b: kalan verify
        home, proje = kur(tmp / "b", f'"{sys.executable}" -c "import sys; sys.exit(1)"')
        r = kos(home, proje, "deneme", "--dry-run")
        if r.returncode != 1 or "KALDI" not in r.stdout:
            hatalar.append(f"kalan verify: exit={r.returncode}\n{r.stdout}")

        # 4: komut bulunamadi -> exit 2, sicile yazma
        home, proje = kur(tmp / "c", "boyle_bir_komut_yok_zzz --x")
        r = kos(home, proje, "deneme")   # dry-run DEGIL: yazmamasi gerek
        if r.returncode != 2 or "KOSAMADI" not in r.stdout:
            hatalar.append(f"kosamadi yolu: exit={r.returncode}\n{r.stdout}{r.stderr}")
        if (home / "LOG_CAGRISI").exists():
            hatalar.append("KOSAMADI durumunda sicile yazdi!")

        # 4b: program ciktisinda "File not found" gecen GERCEK bir KALDI, KOSAMADI
        # sayilmamali (2026-09-20'de Godot ile yasandi)
        sahte = tmp / "kalan_ama_kosabilen.py"
        sahte.write_text("print('ERROR: File not found')\nraise SystemExit(1)\n", encoding="utf-8")
        home, proje = kur(tmp / "c2", f'"{sys.executable}" "{sahte}"')
        r = kos(home, proje, "deneme", "--dry-run")
        if r.returncode != 1 or "KALDI" not in r.stdout or "KOSAMADI" in r.stdout:
            hatalar.append(f"'File not found' ciktili gercek KALDI yanlis siniflandi: "
                           f"exit={r.returncode}\n{r.stdout}")

        # 5: gercek log cagrisi dogru argumanlarla
        home, proje = kur(tmp / "d", f'"{sys.executable}" -c "import sys; sys.exit(0)"')
        r = kos(home, proje, "deneme", "--review-min", "3", "--autonomous", "--note", "t")
        log = home / "LOG_CAGRISI"
        if not log.exists():
            hatalar.append(f"brain log cagrilmadi\n{r.stdout}{r.stderr}")
        else:
            argv = log.read_text(encoding="utf-8")
            for bekle in ("log", "--project test-projesi", "--skill deneme",
                          "--result pass", "--review-min 3", "--autonomous"):
                if bekle not in argv:
                    hatalar.append(f"log argumani eksik: {bekle!r}  ->  {argv}")

    if hatalar:
        print("KALDI:", file=sys.stderr)
        for h in hatalar:
            print("  - " + h, file=sys.stderr)
        return 1
    print("GECTI: kos 6 davranisi da dogru (proje bulma, gecti/kaldi, dry-run, kosamadi, sahte-kosamadi, log argumanlari)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
