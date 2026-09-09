#!/usr/bin/env python3
"""anonim-export: beceri dogrulama testi. Cikis kodu 0 = gecti, 0 disi = kaldi.

Bu test gercek sicili OKUMAZ. Gecici klasorde sahte bir brain-home kurar ve
export hattinin uc sozlesmesini dogrular:
  1. Gizlilik: ciktiya yerel yol ve e-posta sizmaz (not alanlari dahil).
  2. Determinizm: ayni veri -> iki kosuda bit-bit ayni cikti (SHA256 esit).
  3. Takma ad kararlıligi: ayni proje her kosuda ayni P-xxxx kodunu alir.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "scripts" / "brain_export.py"

FAKE_PROJECTS = {
    "kutun-arinisi": {
        "path": "C:\\Users\\kullanici\\Tunga",
        "type": "godot",
        "tags": ["gdscript", "rpg"],
    },
    "gokyazi": {
        "path": "C:\\Users\\kullanici\\YAZGI",
        "type": "flutter",
        "tags": ["dart", "mobile"],
    },
}

FAKE_RUNS = (
    '{"ts": "2026-09-02T11:02:58+00:00", "project": "gokyazi", "skill": "flutter-test-kos", '
    '"result": "pass", "autonomous": true, "review_min": 3.0, '
    '"note": "rapor: C:\\\\Users\\\\kullanici\\\\YAZGI altinda, sorun ali@ornek.com a bildirildi"}\n'
    '{"ts": "2026-09-03T09:00:00+00:00", "project": "kutun-arinisi", "skill": "godot-test-runner", '
    '"result": "fail", "autonomous": false, "review_min": 12.5, "note": ""}\n'
)

FAKE_EVAL = {
    "ts": "2026-09-02T09:42:37+00:00",
    "project": "kutun-arinisi",
    "passed": 8,
    "total": 10,
    "pass_rate": 0.8,
    "results": [{"id": "KA-01", "ok": True, "detail": "exit=0", "kind": "regression"}],
}


def make_fake_home(root: Path) -> Path:
    home = root / "brain-home"
    (home / "memory" / "runs").mkdir(parents=True)
    (home / "memory" / "evals").mkdir(parents=True)
    (home / "projects.json").write_text(
        json.dumps(FAKE_PROJECTS, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (home / "memory" / "runs" / "2026-09.jsonl").write_text(FAKE_RUNS, encoding="utf-8")
    (home / "memory" / "evals" / "20260902-094237-kutun-arinisi.json").write_text(
        json.dumps(FAKE_EVAL, ensure_ascii=False), encoding="utf-8"
    )
    return home


def run_export(home: Path, out: Path) -> int:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--brain-home", str(home), "--out", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    if proc.returncode != 0:
        print(f"KALDI: export cikis kodu {proc.returncode}", file=sys.stderr)
        print(proc.stdout[-800:], file=sys.stderr)
        print(proc.stderr[-800:], file=sys.stderr)
    return proc.returncode


def sha256_dir(d: Path) -> dict:
    hashes = {}
    for p in sorted(d.rglob("*")):
        if p.is_file():
            hashes[str(p.relative_to(d))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes


def main() -> int:
    if not SCRIPT.exists():
        print("KALDI: scripts/brain_export.py bulunamadi", file=sys.stderr)
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="anonim-export-test-"))
    try:
        home = make_fake_home(tmp)
        out1, out2 = tmp / "cikti-1", tmp / "cikti-2"

        if run_export(home, out1) != 0:
            return 1
        if run_export(home, out2) != 0:
            return 1

        h1, h2 = sha256_dir(out1), sha256_dir(out2)
        if h1 != h2:
            farkli = [k for k in set(h1) | set(h2) if h1.get(k) != h2.get(k)]
            print(f"KALDI: cikti deterministik degil, farkli dosyalar: {farkli}", file=sys.stderr)
            return 1

        leak_files = []
        for p in out1.rglob("*"):
            if not p.is_file():
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            if "C:\\Users" in text or "ali@ornek.com" in text:
                leak_files.append(p.name)
        if leak_files:
            print(f"KALDI: gizlilik sizmasi: {leak_files}", file=sys.stderr)
            return 1

        runs = [json.loads(l) for l in (out1 / "runs.jsonl").read_text(encoding="utf-8").splitlines() if l]
        kodlar = {r["project"] for r in runs if r["project"]}
        kotu = [k for k in kodlar if not re.fullmatch(r"P-[0-9a-f]{4}", k)]
        if kotu:
            print(f"KALDI: takma ad formati bozuk: {kotu}", file=sys.stderr)
            return 1
        if len(kodlar) < 2:
            print("KALDI: iki proje tek koda indirgenmis", file=sys.stderr)
            return 1

        notes = " ".join(r.get("note", "") for r in runs)
        if "[PATH]" not in notes:
            print("KALDI: yol temizligi calismadi (not alaninda [PATH] bekleniyordu)", file=sys.stderr)
            return 1

        print("GECTI: gizlilik temizi, cikti deterministik, takma adlar kararli.")
        print(f"  dosya sayisi: {len(h1)} | kosu: {len(runs)} | takma adlar: {sorted(kodlar)}")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
