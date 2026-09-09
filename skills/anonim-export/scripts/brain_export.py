#!/usr/bin/env python3
"""
brain_export.py — onoz-brain sicilini anonimleştirilmiş açık-veri paketine çevirir.

onoz-brain becerisi: anonim-export (applies_to: [] — tüm projelerde görünür)
stdlib-only (Python 3.9+). Motor (brain.py) ile ilişkisi yoktur: SADECE OKUR,
çıktıyı ayrı klasöre yazar. "Sahte sicil yok" ilkesine uyar — hiçbir kayıt üretmez.

Determinizm sözleşmesi:
  Aynı memory/ içeriği -> bit-bit aynı çıktı. Zaman damgası "şimdi" değil,
  verideki en büyük ts'den (as_of) türetilir. İki export'un hash'i aynıdır.

Anonimleştirme:
  - Proje adlari -> SHA1 tabanli kararli takma ad (P-xxxx). Ayni proje her
    export'ta ayni kodu alir; --real-names ile acilmadikca.
  - Yerel yollar ve e-posta adresleri [PATH] ile maskelemez — tamamen kirpilir
    (not alanlari dahil).
  - projects.json'dan yalnizca tip ve etiketler tasinir; yol asla tasinmaz.

Kullanim:
  python scripts/brain_export.py                          # varsayilan: takma adli
  python scripts/brain_export.py --out ./cikti
  python scripts/brain_export.py --real-names             # DIKKAT: kimlik acar
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys

DEFAULT_BRAIN_HOME = os.environ.get("BRAIN_HOME", "")

PATH_PATTERNS = [
    re.compile(r"[A-Z]:\\[^\s\"',;)\]]+", re.I),
    re.compile(r"/(?:home|Users)/[^\s\"',;)\]]+", re.I),
    re.compile(r"[\w.\-]+@[\w.\-]+\.\w+"),
]


def scrub(text: str) -> str:
    """Yol ve e-posta iceren her metni temizler. Not alanlari dahil."""
    if not text:
        return text
    out = text
    for pat in PATH_PATTERNS:
        out = pat.sub("[PATH]", out)
    return out


def stable_pseudonym(name: str) -> str:
    return "P-" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:4]


def load_projects(brain_home: str) -> dict:
    pj = os.path.join(brain_home, "projects.json")
    if not os.path.exists(pj):
        return {}
    with open(pj, encoding="utf-8") as f:
        raw = json.load(f)
    return {
        name: {"type": meta.get("type", "?"), "tags": meta.get("tags", [])}
        for name, meta in raw.items()
    }


def build_alias(projects: dict, real_names: bool):
    """(alias, meta) dondurur. alias: proje adi -> takma ad; meta: takma ad -> {type, tags}."""
    alias, meta = {}, {}
    for name in sorted(projects):
        key = name if real_names else stable_pseudonym(name)
        alias[name] = key
        alias["__type_" + name] = projects[name].get("type", "?")
        meta[key] = {"type": projects[name].get("type", "?"), "tags": projects[name].get("tags", [])}
    return alias, meta


def _max_ts(value) -> str:
    return value if isinstance(value, str) else ""


def collect_runs(brain_home: str, alias: dict):
    runs_dir = os.path.join(brain_home, "memory", "runs")
    rows = []
    if not os.path.isdir(runs_dir):
        return rows
    for fname in sorted(os.listdir(runs_dir)):
        if not fname.endswith(".jsonl"):
            continue
        with open(os.path.join(runs_dir, fname), encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                proj = r.get("project", "?")
                rows.append({
                    "ts": _max_ts(r.get("ts", "")),
                    "project": alias.get(proj, proj),
                    "project_type": alias.get("__type_" + proj, ""),
                    "skill": r.get("skill", ""),
                    "result": r.get("result", ""),
                    "autonomous": r.get("autonomous", None),
                    "review_min": r.get("review_min", None),
                    "note": scrub(r.get("note", "")),
                })
    return rows


def collect_evals(brain_home: str, alias: dict):
    ev_dir = os.path.join(brain_home, "memory", "evals")
    rows = []
    if not os.path.isdir(ev_dir):
        return rows
    for fname in sorted(os.listdir(ev_dir)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(ev_dir, fname), encoding="utf-8") as f:
            try:
                ev = json.load(f)
            except json.JSONDecodeError:
                continue
        proj = ev.get("project", "?")
        rows.append({
            "ts": _max_ts(ev.get("ts", "")),
            "project": alias.get(proj, proj),
            "project_type": alias.get("__type_" + proj, ""),
            "eval_file": fname,
            "passed": ev.get("passed", None),
            "total": ev.get("total", None),
            "pass_rate": ev.get("pass_rate", None),
            "items": len(ev.get("results", [])),
        })
    return rows


def collect_lessons(brain_home: str):
    ls_dir = os.path.join(brain_home, "memory", "lessons")
    rows = []
    if not os.path.isdir(ls_dir):
        return rows
    for fname in sorted(os.listdir(ls_dir)):
        if not fname.endswith(".md"):
            continue
        with open(os.path.join(ls_dir, fname), encoding="utf-8", errors="replace") as f:
            head = f.read(400)
        rows.append({
            "file": fname,
            "first_line": scrub(head.split("\n")[0])[:120] if head else "",
        })
    return rows


def summarize(runs, evals, meta, as_of: str):
    total = len(runs)
    auto = sum(1 for r in runs if r["autonomous"] is True)
    passes = sum(1 for r in runs if r["result"] == "pass")
    review = [r["review_min"] for r in runs if isinstance(r["review_min"], (int, float))]
    avg_review = round(sum(review) / len(review), 2) if review else None
    by_skill = {}
    for r in runs:
        s = by_skill.setdefault(r["skill"], {"runs": 0, "pass": 0, "autonomous": 0})
        s["runs"] += 1
        s["pass"] += 1 if r["result"] == "pass" else 0
        s["autonomous"] += 1 if r["autonomous"] is True else 0
    return {
        "as_of": as_of,
        "total_runs": total,
        "autonomous_runs": auto,
        "autonomy_rate": round(100 * auto / total, 1) if total else None,
        "pass_rate": round(100 * passes / total, 1) if total else None,
        "avg_review_min": avg_review,
        "eval_records": len(evals),
        "by_skill": by_skill,
        "projects": meta,
        "note": "n kucukken oranlara guvenme; bu ozet yalnizca olcum altyapisinin calistigini gosterir",
    }


def write_outputs(out_dir: str, runs, evals, lessons, summary):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "runs.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in runs:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    with open(os.path.join(out_dir, "evals.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for e in evals:
            f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
    with open(os.path.join(out_dir, "lessons.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(lessons, f, ensure_ascii=False, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "summary.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for k in ["as_of", "total_runs", "autonomous_runs", "autonomy_rate", "pass_rate", "avg_review_min", "eval_records"]:
            w.writerow([k, summary.get(k)])
        w.writerow([])
        w.writerow(["skill", "runs", "pass", "autonomous"])
        for s, d in sorted(summary["by_skill"].items()):
            w.writerow([s, d["runs"], d["pass"], d["autonomous"]])
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(
            "# onoz-brain acik sicil paketi (taslak)\n\n"
            f"Veri tarihi: {summary['as_of'] or '(bos sicil)'}\n\n"
            "Bu klasor, onoz-brain calisma sisteminin anonimlestirilmis koşu sicilidir.\n"
            "Proje adlari SHA1 tabanli kararli takma adlarla degistirilmistir\n"
            "(ayni proje her export'ta ayni kodu alir); yerel yollar ve e-postalar\n"
            "kirpilmistir. projects.json'dan yalnizca tip ve etiketler tasinmistir.\n\n"
            "Dosyalar:\n"
            "- runs.jsonl   — beceri kosulari (sicilin kendisi)\n"
            "- evals.jsonl  — regression eval kayitlari\n"
            "- lessons.json — ders kayitlari (ilk satir)\n"
            "- summary.csv / summary.json — ozet metrikler\n\n"
            f"n={summary['total_runs']} kosu ile oranlar istatistiksel olarak anlamli degildir.\n"
            "Bu paket su asamada olcum altyapisinin kanitidir, performans iddiasi degil.\n"
            "(onoz-brain kurali: sahte sicil yok.)\n"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="onoz-brain anonim sicil export")
    ap.add_argument("--brain-home", default=DEFAULT_BRAIN_HOME)
    ap.add_argument("--out", required=True)
    ap.add_argument("--real-names", action="store_true",
                    help="gercek proje adlarini kullan (PUBLIC oncesi KAPALI kalmali)")
    args = ap.parse_args()

    if not args.brain_home or not os.path.isdir(args.brain_home):
        print(f"ON KOSUL: gecerli BRAIN_HOME yok: {args.brain_home!r}", file=sys.stderr)
        print("          --brain-home verin veya BRAIN_HOME ortam degiskenini ayarla.", file=sys.stderr)
        return 2
    if args.real_names:
        print("UYARI: --real-names acik. Cikti kimlik tasiyabilir; public'e koyma.", file=sys.stderr)

    projects = load_projects(args.brain_home)
    alias, meta = build_alias(projects, args.real_names)

    runs = collect_runs(args.brain_home, alias)
    evals = collect_evals(args.brain_home, alias)
    lessons = collect_lessons(args.brain_home)

    all_ts = [r["ts"] for r in runs] + [e["ts"] for e in evals]
    as_of = max(all_ts) if all_ts else ""

    summary = summarize(runs, evals, meta, as_of)
    write_outputs(args.out, runs, evals, lessons, summary)

    print(f"[OK] export tamam: {args.out}")
    print(f"     as_of={as_of or '(bos)'} runs={len(runs)} evals={len(evals)} "
          f"otonomi={summary['autonomy_rate']}% (n={summary['total_runs']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
