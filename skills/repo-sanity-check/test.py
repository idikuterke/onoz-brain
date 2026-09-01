#!/usr/bin/env python3
"""repo-sanity-check: build + lint + test zincirini tek komutta kosar.

Proje tipi marker dosyalarindan cikarilir (--type ile zorlanabilir):
  project.godot -> godot, pubspec.yaml -> flutter, package.json -> web,
  pyproject.toml/setup.*/pytest.ini/tests/ -> python-tool

Cikis kodlari:
  0 = uygulanabilir adimlardan en az biri kostu ve hepsi gecti
  1 = kosan bir adim kaldi (somut bir hata bulundu)
  2 = on kosul eksik: --project verilmedi, proje taninamadi, araci eksik
      olan adim var veya hicbir adim uygulanabilir degil.
      Araci olmayan adim asla 'gecti' sayilmaz.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

READY = "ready"
SKIP_TOOL = "arac_yok"
SKIP_ABSENT = "yok"


def detect_type(project: Path) -> str | None:
    if (project / "project.godot").exists():
        return "godot"
    if (project / "pubspec.yaml").exists():
        return "flutter"
    if (project / "package.json").exists():
        return "web"
    markers = ("pyproject.toml", "setup.py", "setup.cfg", "pytest.ini", "tox.ini")
    if any((project / m).exists() for m in markers) or (project / "tests").is_dir():
        return "python-tool"
    return None


def has_pytest_files(project: Path) -> bool:
    for pat in ("test_*.py", "*_test.py"):
        if any(project.rglob(pat)):
            return True
    return False


def build_chain(ptype: str, project: Path) -> list[dict]:
    """Adimlar: {ad, durum, sebep, cmd}. cmd sadece READY adimlarda dolu."""
    steps: list[dict] = []

    def add(name: str, tool: str | None, args: list[str], applicable: bool, sebep: str):
        if not applicable:
            steps.append({"ad": name, "durum": SKIP_ABSENT, "sebep": sebep, "cmd": None})
            return
        if tool is not None:
            exe = shutil.which(tool)
            if exe is None:
                steps.append({"ad": name, "durum": SKIP_TOOL,
                              "sebep": f"'{tool}' PATH'te yok", "cmd": None})
                return
            args = [exe] + args
        steps.append({"ad": name, "durum": READY, "sebep": "", "cmd": args})

    if ptype == "godot":
        add("godot-import", "godot", ["--headless", "--path", str(project), "--import"],
            True, "")
        run_tests = project / "tests" / "run_tests.gd"
        add("godot-test", "godot",
            ["--headless", "--path", str(project), "-s", "res://tests/run_tests.gd"],
            run_tests.exists(), "tests/run_tests.gd yok (test adimi uygulanamaz)")
    elif ptype == "flutter":
        add("flutter-analyze", "flutter", ["analyze"], True, "")
        has_tests = bool(list((project / "test").glob("*_test.dart"))) \
            if (project / "test").is_dir() else False
        add("flutter-test", "flutter", ["test"], has_tests,
            "test/ altinda *_test.dart yok (test adimi uygulanamaz)")
    elif ptype == "web":
        scripts: dict = {}
        try:
            scripts = json.loads((project / "package.json").read_text(encoding="utf-8"))
            scripts = scripts.get("scripts", {}) or {}
        except (json.JSONDecodeError, OSError):
            scripts = {}
        add("web-lint", "npm", ["run", "lint"], "lint" in scripts,
            "package.json'da 'lint' script'i yok")
        add("web-build", "npm", ["run", "build"], "build" in scripts,
            "package.json'da 'build' script'i yok")
        add("web-test", "npm", ["test"], "test" in scripts,
            "package.json'da 'test' script'i yok")
    elif ptype == "python-tool":
        add("pytest", "pytest", ["-q"], has_pytest_files(project),
            "test_*.py / *_test.py bulunamadi (test adimi uygulanamaz)")
    return steps


def run_step(step: dict, project: Path, timeout: int) -> None:
    try:
        proc = subprocess.run(step["cmd"], cwd=str(project), capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              timeout=timeout)
        step["durum"] = "gecti" if proc.returncode == 0 else "kaldi"
        step["cikis"] = proc.returncode
        step["cikti"] = (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        step["durum"] = "kaldi"
        step["cikis"] = "TIMEOUT"
        step["cikti"] = f"{timeout}s icinde bitmedi (timeout)."


def main() -> int:
    ap = argparse.ArgumentParser(
        description="build + lint + test zincirini tek komutta kosar")
    ap.add_argument("--project", required=True, help="proje kok dizini")
    ap.add_argument("--type", choices=["godot", "flutter", "web", "python-tool"],
                    help="proje tipini zorla (varsayilan: marker tespiti)")
    ap.add_argument("--timeout", type=int, default=300, help="adim basi sn")
    args = ap.parse_args()

    project = Path(args.project).expanduser()
    if not project.is_dir():
        print(f"HATA: proje dizini yok: {project}", file=sys.stderr)
        return 2

    ptype = args.type or detect_type(project)
    if ptype is None:
        print(f"HATA: proje tipi taninamadi: {project}", file=sys.stderr)
        print("      Marker dosyalarindan hicbiri yok; --type ile zorlayin.",
              file=sys.stderr)
        return 2

    steps = build_chain(ptype, project)
    if not any(s["durum"] == READY for s in steps):
        print(f"KALDI: proje tipi '{ptype}' icin uygulanabilir adim yok.", file=sys.stderr)
        for s in steps:
            print(f"  - {s['ad']}: {s['sebep']}", file=sys.stderr)
        return 2

    for s in steps:
        if s["durum"] == READY:
            run_step(s, project, args.timeout)
        print(f"[{s['durum']:^9}] {s['ad']}"
              + (f"  (exit {s.get('cikis')})" if "cikis" in s else "")
              + (f"  -> {s['sebep']}" if s["sebep"] else ""))

    failed = [s for s in steps if s["durum"] in ("gecti", "kaldi") and s["durum"] == "kaldi"]
    tool_missing = [s for s in steps if s["durum"] == SKIP_TOOL]
    ran = [s for s in steps if s["durum"] in ("gecti", "kaldi")]

    for s in failed:
        tail = s.get("cikti", "").strip().splitlines()[-15:]
        for line in tail:
            print("  | " + line, file=sys.stderr)

    if failed:
        print(f"KALDI: {len(failed)} adim kaldi ({ptype})", file=sys.stderr)
        return 1
    if tool_missing:
        print(f"ON KOSUL: {len(tool_missing)} adimin araci yok -> 2", file=sys.stderr)
        return 2
    print(f"GECTI: {len(ran)} adim temiz ({ptype})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
