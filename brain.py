#!/usr/bin/env python3
"""
brain - ONOZ Labs beceri kayit ve yetki sistemi.

Tek merkezde duran beceri kutuphanesini birden fazla projeye servis eder,
her kullanimin sicilini tutar ve becerileri kanita dayali olarak terfi ettirir.

Bagimlilik: yok (sadece Python 3.9+ standart kutuphane).
Kurulum:    BRAIN_HOME ortam degiskeni, yoksa ~/onoz-brain
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------
# Sabitler
# --------------------------------------------------------------------------

LEVELS = ["L0", "L1", "L2", "L3"]

LEVEL_DESC = {
    "L0": "Onerir, sen uygularsin",
    "L1": "Uygular ve branch acar, sen merge edersin",
    "L2": "Uygular, test gecerse otomatik merge, haftalik denetim",
    "L3": "Kendi gorevini kendi uretir, aylik denetim",
}

# Terfi esikleri. Kaynak: yetki merdiveni sozlesmesi (README).
PROMOTION_RULES = {
    "L0": {"next": "L1", "min_runs": 10, "min_pass_rate": 0.80},
    "L1": {"next": "L2", "min_runs": 20, "min_pass_rate": 0.90},
    "L2": {"next": "L3", "min_runs": 50, "min_pass_rate": 0.95},
}

# Sessiz hata = testi gecti ama sonuc yanlis. Terfiyi durdurur, seviye dusurur.
SILENT_ERROR_WINDOW = 20

RESULTS = ("pass", "fail", "silent_error")

STALE_DAYS = 60  # bu sure cagrilmayan beceri arsive aday


# --------------------------------------------------------------------------
# Yardimcilar
# --------------------------------------------------------------------------

class BrainError(Exception):
    """Kullaniciya gosterilecek, beklenen hata."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def brain_home() -> Path:
    raw = os.environ.get("BRAIN_HOME")
    root = Path(raw).expanduser() if raw else Path.home() / "onoz-brain"
    return root.resolve()


def read_json(path: Path, default=None):
    if not path.exists():
        if default is None:
            raise BrainError(f"Dosya yok: {path}")
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BrainError(f"Bozuk JSON: {path} ({exc})") from exc


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)  # atomik yazim: yarim kalan dosya birakmaz


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    if not slug:
        raise BrainError(f"Gecersiz isim: {name!r}")
    return slug


def days_since(iso: str) -> int:
    try:
        then = datetime.fromisoformat(iso)
    except ValueError:
        return 10**6
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    return max(0, (datetime.now(timezone.utc) - then).days)


# --------------------------------------------------------------------------
# Depo katmani
# --------------------------------------------------------------------------

class Brain:
    def __init__(self, root: Path):
        self.root = root
        self.skills_dir = root / "skills"
        self.runs_dir = root / "memory" / "runs"
        self.lessons_dir = root / "memory" / "lessons"
        self.projects_file = root / "projects.json"

    # -- kurulum ----------------------------------------------------------

    def init(self) -> None:
        for d in (self.skills_dir, self.runs_dir, self.lessons_dir, self.root / "evals"):
            d.mkdir(parents=True, exist_ok=True)
        if not self.projects_file.exists():
            write_json(self.projects_file, {})

    def require(self) -> None:
        if not self.skills_dir.exists():
            raise BrainError(
                f"BRAIN_HOME bulunamadi: {self.root}\n"
                f"Once 'python brain.py init' calistir veya BRAIN_HOME ayarla."
            )

    # -- projeler ---------------------------------------------------------

    def projects(self) -> dict:
        return read_json(self.projects_file, default={})

    def add_project(self, name: str, path: Path, ptype: str, tags: list[str]) -> dict:
        if not path.exists():
            raise BrainError(f"Proje dizini yok: {path}")
        projects = self.projects()
        entry = {
            "path": str(path.resolve()),
            "type": ptype,
            "tags": sorted(set(tags) | {ptype}),
            "linked": now_iso(),
        }
        projects[name] = entry
        write_json(self.projects_file, projects)
        # Projeye tek bir isaret dosyasi birak. Symlink yok -> Windows/Linux ayni.
        write_json(path / ".brain.json", {"project": name, "type": ptype, "tags": entry["tags"]})
        return entry

    def project(self, name: str) -> dict:
        projects = self.projects()
        if name not in projects:
            known = ", ".join(sorted(projects)) or "(kayitli proje yok)"
            raise BrainError(f"Proje bulunamadi: {name}\nKayitli: {known}")
        return projects[name]

    # -- beceriler --------------------------------------------------------

    def skills(self) -> list[dict]:
        out = []
        if not self.skills_dir.exists():
            return out
        for d in sorted(self.skills_dir.iterdir()):
            if not d.is_dir() or d.name.startswith("_"):
                continue
            meta_path = d / "skill.json"
            if not meta_path.exists():
                print(f"[uyari] skill.json yok, atlandi: {d.name}", file=sys.stderr)
                continue
            meta = read_json(meta_path)
            meta["_dir"] = d
            meta.setdefault("id", d.name)
            meta.setdefault("level", "L0")
            meta.setdefault("applies_to", [])
            meta.setdefault("tags", [])
            out.append(meta)
        return out

    def skill(self, skill_id: str) -> dict:
        for s in self.skills():
            if s["id"] == skill_id:
                return s
        known = ", ".join(s["id"] for s in self.skills()) or "(beceri yok)"
        raise BrainError(f"Beceri bulunamadi: {skill_id}\nKayitli: {known}")

    def save_skill(self, meta: dict) -> None:
        d = meta.pop("_dir")
        write_json(d / "skill.json", meta)
        meta["_dir"] = d

    def create_skill(self, name: str, applies_to: list[str], tags: list[str]) -> Path:
        skill_id = slugify(name)
        target = self.skills_dir / skill_id
        if target.exists():
            raise BrainError(f"Bu beceri zaten var: {skill_id}")
        template = self.skills_dir / "_template"
        target.mkdir(parents=True)

        meta = {
            "id": skill_id,
            "level": "L0",
            "applies_to": applies_to,
            "tags": tags,
            "verify": "python test.py",
            "created": now_iso(),
            "archived": False,
        }
        write_json(target / "skill.json", meta)

        if (template / "SKILL.md").exists():
            body = (template / "SKILL.md").read_text(encoding="utf-8")
            body = body.replace("{{ID}}", skill_id).replace("{{NAME}}", name)
        else:
            body = f"# {name}\n\n## Ne zaman kullanilir\n\n## Kullanilmaz\n\n## Dogrulama\n"
        (target / "SKILL.md").write_text(body, encoding="utf-8")

        if (template / "test.py").exists():
            (target / "test.py").write_text(
                (template / "test.py").read_text(encoding="utf-8"), encoding="utf-8"
            )
        return target

    # -- sicil ------------------------------------------------------------

    def log_run(self, record: dict) -> None:
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        path = self.runs_dir / f"{month}.jsonl"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def runs(self, skill_id: str | None = None, project: str | None = None) -> list[dict]:
        out = []
        if not self.runs_dir.exists():
            return out
        for path in sorted(self.runs_dir.glob("*.jsonl")):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[uyari] bozuk kayit atlandi: {path.name}:{lineno}", file=sys.stderr)
                    continue
                if skill_id and rec.get("skill") != skill_id:
                    continue
                if project and rec.get("project") != project:
                    continue
                out.append(rec)
        return out


# --------------------------------------------------------------------------
# Istatistik / terfi mantigi
# --------------------------------------------------------------------------

def summarize(runs: list[dict]) -> dict:
    total = len(runs)
    if total == 0:
        return {"total": 0, "pass_rate": 0.0, "silent": 0, "autonomy": 0.0, "avg_review_min": 0.0}
    passed = sum(1 for r in runs if r.get("result") == "pass")
    silent = sum(1 for r in runs if r.get("result") == "silent_error")
    autonomous_pass = sum(1 for r in runs if r.get("result") == "pass" and r.get("autonomous"))
    review = [float(r.get("review_min", 0) or 0) for r in runs]
    return {
        "total": total,
        "pass_rate": passed / total,
        "silent": silent,
        "autonomy": autonomous_pass / total,
        "avg_review_min": sum(review) / total,
    }


def evaluate_promotion(level: str, runs: list[dict]) -> tuple[str, str]:
    """(karar, gerekce) dondurur. karar: promote | hold | demote."""
    recent = runs[-SILENT_ERROR_WINDOW:]
    if any(r.get("result") == "silent_error" for r in recent):
        idx = LEVELS.index(level)
        if idx > 0:
            return "demote", f"son {len(recent)} kosuda sessiz hata var -> seviye dusuruluyor"
        return "hold", "sessiz hata var, L0'da kaliyor"

    rule = PROMOTION_RULES.get(level)
    if rule is None:
        return "hold", "en ust seviye"

    stats = summarize(runs)
    if stats["total"] < rule["min_runs"]:
        return "hold", f"{stats['total']}/{rule['min_runs']} kosu"
    if stats["pass_rate"] < rule["min_pass_rate"]:
        return "hold", f"basari %{stats['pass_rate']*100:.0f} < %{rule['min_pass_rate']*100:.0f}"
    return "promote", f"{stats['total']} kosu, basari %{stats['pass_rate']*100:.0f}"


def when_to_use(skill_dir: Path) -> str:
    """SKILL.md icindeki 'Ne zaman kullanilir' bolumunu cikarir."""
    md = skill_dir / "SKILL.md"
    if not md.exists():
        return "(SKILL.md yok)"
    lines = md.read_text(encoding="utf-8").splitlines()
    buf, capturing = [], False
    for line in lines:
        if line.startswith("## "):
            if capturing:
                break
            capturing = "ne zaman" in line.lower()
            continue
        if capturing and line.strip() and not line.lstrip().startswith("<!--"):
            buf.append(line.strip())
    return " ".join(buf).strip() or "(tanimsiz)"


# --------------------------------------------------------------------------
# Komutlar
# --------------------------------------------------------------------------

def cmd_init(brain: Brain, args) -> int:
    brain.init()
    print(f"BRAIN_HOME hazir: {brain.root}")
    print("Sonraki adim: python brain.py link <proje-adi> <yol> --type godot")
    return 0


def cmd_link(brain: Brain, args) -> int:
    brain.require()
    entry = brain.add_project(args.name, Path(args.path).expanduser(), args.type, args.tag or [])
    print(f"Baglandi: {args.name} -> {entry['path']} (tip: {entry['type']})")
    print(f"Proje icine .brain.json yazildi. Symlink yok, tasinabilir.")
    return 0


def cmd_new(brain: Brain, args) -> int:
    brain.require()
    path = brain.create_skill(args.name, args.applies_to or [], args.tag or [])
    print(f"Beceri olusturuldu: {path}")
    print("SIRADAKI ZORUNLU ADIM: SKILL.md'yi doldur + test.py yaz.")
    print("Testi olmayan beceri kutuphaneye kabul edilmez.")
    return 0


def cmd_list(brain: Brain, args) -> int:
    brain.require()
    skills = brain.skills()
    if args.project:
        proj = brain.project(args.project)
        ptags = set(proj["tags"])
        skills = [s for s in skills if not s["applies_to"] or ptags & set(s["applies_to"])]
    if args.level:
        skills = [s for s in skills if s["level"] == args.level]
    if not skills:
        print("Kriterlere uyan beceri yok.")
        return 0

    print(f"{'SEVIYE':<7} {'BECERI':<34} {'KOSU':>5} {'BASARI':>7} {'SON':>6}")
    print("-" * 64)
    for s in sorted(skills, key=lambda x: (LEVELS.index(x["level"]), x["id"]), reverse=True):
        runs = brain.runs(skill_id=s["id"])
        st = summarize(runs)
        last = runs[-1]["ts"] if runs else s.get("created", "")
        age = days_since(last) if last else "-"
        flag = " [BAYAT]" if isinstance(age, int) and age > STALE_DAYS and runs else ""
        rate = f"%{st['pass_rate']*100:.0f}" if st["total"] else "-"
        print(f"{s['level']:<7} {s['id']:<34} {st['total']:>5} {rate:>7} {str(age)+'g':>6}{flag}")
    return 0


def cmd_context(brain: Brain, args) -> int:
    """Ajana verilecek brifingi uretir. Model bagimsiz: stdout -> istedigin araca boru."""
    brain.require()
    proj = brain.project(args.project)
    ptags = set(proj["tags"])
    skills = [s for s in brain.skills()
              if not s.get("archived") and (not s["applies_to"] or ptags & set(s["applies_to"]))]

    print(f"# Beceri brifingi: {args.project}")
    print(f"\nProje tipi: {proj['type']} | Etiketler: {', '.join(sorted(ptags))}")
    print(f"Dizin: {proj['path']}\n")
    print("## Yetki kurallari\n")
    for lvl in LEVELS:
        print(f"- **{lvl}** — {LEVEL_DESC[lvl]}")
    print("\nBir beceriyi kendi seviyesinin uzerinde kullanma. "
          "Seviyesi belirsizse L0 varsay.\n")

    for lvl in reversed(LEVELS):
        group = [s for s in skills if s["level"] == lvl]
        if not group:
            continue
        print(f"## {lvl} becerileri\n")
        for s in sorted(group, key=lambda x: x["id"]):
            st = summarize(brain.runs(skill_id=s["id"]))
            print(f"### {s['id']}")
            print(f"- Ne zaman: {when_to_use(s['_dir'])}")
            print(f"- Dogrulama: `{s.get('verify', '(tanimsiz)')}`")
            print(f"- Sicil: {st['total']} kosu, basari %{st['pass_rate']*100:.0f}, "
                  f"sessiz hata {st['silent']}")
            print(f"- Dosya: {s['_dir']}\n")

    lessons = sorted(brain.lessons_dir.glob("*.md"))
    if lessons:
        print("## Onceki hatalardan cikan kurallar\n")
        for l in lessons[-15:]:
            print(l.read_text(encoding="utf-8").strip() + "\n")
    return 0


def cmd_log(brain: Brain, args) -> int:
    brain.require()
    brain.skill(args.skill)          # dogrula: olmayan beceriye sicil yazma
    brain.project(args.project)      # dogrula: olmayan projeye sicil yazma
    if args.result not in RESULTS:
        raise BrainError(f"result su degerlerden biri olmali: {', '.join(RESULTS)}")
    if args.review_min < 0:
        raise BrainError("review-min negatif olamaz")

    record = {
        "ts": now_iso(),
        "project": args.project,
        "skill": args.skill,
        "result": args.result,
        "autonomous": bool(args.autonomous),
        "review_min": args.review_min,
        "note": args.note or "",
    }
    brain.log_run(record)
    print(f"Kayit alindi: {args.skill} -> {args.result} ({args.review_min} dk inceleme)")

    if args.result == "silent_error":
        print("!! SESSIZ HATA. Bu becerinin terfisi durdu ve seviyesi dusurulecek.")
        print("   'python brain.py lesson' ile kurali yaz, yoksa ayni hata tekrarlar.")
    return 0


def cmd_lesson(brain: Brain, args) -> int:
    brain.require()
    brain.lessons_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = brain.lessons_dir / f"{stamp}-{slugify(args.skill)}.md"
    path.write_text(
        f"- **{args.skill}**: {args.rule}\n", encoding="utf-8"
    )
    print(f"Kural kaydedildi: {path}")
    print("Bu kural bundan sonra her 'context' ciktisina eklenir.")
    return 0


def cmd_stats(brain: Brain, args) -> int:
    brain.require()
    runs = brain.runs(project=args.project)
    st = summarize(runs)
    scope = f"proje: {args.project}" if args.project else "tum projeler"
    print(f"Sicil ozeti ({scope})\n" + "-" * 40)
    if st["total"] == 0:
        print("Henuz kosu kaydi yok. 'brain.py log' ile baslat.")
        return 0
    print(f"Toplam kosu           : {st['total']}")
    print(f"Otonomi orani         : %{st['autonomy']*100:.1f}   <- ASIL METRIK")
    print(f"Basari orani          : %{st['pass_rate']*100:.1f}")
    print(f"Gorev basi inceleme   : {st['avg_review_min']:.1f} dk   <- DUSMELI")
    print(f"Sessiz hata           : {st['silent']}   <- SIFIR OLMALI")
    if st["silent"] > 0:
        print("\nSessiz hata varken hicbir terfi yapilmaz.")
    return 0


def cmd_promote(brain: Brain, args) -> int:
    brain.require()
    changed = 0
    for s in brain.skills():
        runs = brain.runs(skill_id=s["id"])
        decision, reason = evaluate_promotion(s["level"], runs)
        if decision == "promote":
            new = PROMOTION_RULES[s["level"]]["next"]
            print(f"[TERFI ADAYI] {s['id']}: {s['level']} -> {new} ({reason})")
            if args.apply:
                s["level"] = new
                brain.save_skill(s)
                changed += 1
        elif decision == "demote":
            new = LEVELS[LEVELS.index(s["level"]) - 1]
            print(f"[TENZIL]      {s['id']}: {s['level']} -> {new} ({reason})")
            if args.apply:
                s["level"] = new
                brain.save_skill(s)
                changed += 1
        elif args.verbose:
            print(f"[beklemede]   {s['id']}: {s['level']} ({reason})")

    if not args.apply:
        print("\nSalt okunur calisti. Uygulamak icin: --apply")
        print("Terfiyi sen onaylarsin; sistem sadece veriyi hazirlar.")
    else:
        print(f"\n{changed} beceri seviyesi guncellendi.")
    return 0



def cmd_eval(brain: Brain, args) -> int:
    """Sabit gorev setini calistirir. Sistemin butununun olcum aletidir."""
    brain.require()
    proj = brain.project(args.project)
    path = brain.root / "evals" / args.project / "tasks.jsonl"
    if not path.exists():
        raise BrainError(f"Eval seti yok: {path}")

    tasks = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            tasks.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise BrainError(f"Bozuk eval gorevi {path.name}:{lineno} ({exc})") from exc

    if args.task:
        tasks = [t for t in tasks if t.get("id") == args.task]
        if not tasks:
            raise BrainError(f"Gorev bulunamadi: {args.task}")

    cwd = Path(proj["path"])
    if not cwd.exists():
        raise BrainError(f"Proje dizini kayip: {cwd}")

    env = dict(os.environ, BRAIN_HOME=str(brain.root))
    results = []
    for t in tasks:
        tid, title = t.get("id", "?"), t.get("title", "")
        if args.dry_run:
            flag = " [DUZELTME GEREKIR]" if t.get("needs_adjust") else ""
            print(f"{tid}  {title}{flag}\n      $ {t.get('verify','')}")
            continue
        try:
            proc = subprocess.run(t["verify"], shell=True, cwd=str(cwd), env=env,
                                  capture_output=True, text=True,
                                  timeout=int(t.get("timeout", 120)))
            ok, detail = proc.returncode == 0, f"exit={proc.returncode}"
        except subprocess.TimeoutExpired:
            ok, detail = False, "TIMEOUT"
        except OSError as exc:
            ok, detail = False, f"calistirilamadi: {exc}"
        results.append({"id": tid, "ok": ok, "detail": detail})
        print(f"[{'GECTI' if ok else 'KALDI'}] {tid}  {title}" + ("" if ok else f"  ({detail})"))

    if args.dry_run:
        print(f"\n{len(tasks)} gorev. Calistirmak icin --dry-run'i kaldir.")
        return 0

    passed = sum(1 for r in results if r["ok"])
    total = len(results) or 1
    rate = passed / total
    print(f"\nPASS RATE: {passed}/{len(results)} = %{rate*100:.1f}")

    if args.record:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        out = brain.root / "memory" / "evals" / f"{stamp}-{args.project}.json"
        write_json(out, {"ts": now_iso(), "project": args.project,
                         "passed": passed, "total": len(results),
                         "pass_rate": round(rate, 4), "results": results})
        print(f"Kaydedildi: {out}")
    else:
        print("Kaydetmek icin: --record  (baseline'i mutlaka kaydet)")
    return 0 if passed == len(results) else 1


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="brain", description="ONOZ Labs beceri ve yetki sistemi")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="BRAIN_HOME yapisini olustur").set_defaults(fn=cmd_init)

    sp = sub.add_parser("link", help="Bir projeyi sisteme bagla")
    sp.add_argument("name")
    sp.add_argument("path")
    sp.add_argument("--type", required=True, help="godot | flutter | python | web ...")
    sp.add_argument("--tag", action="append")
    sp.set_defaults(fn=cmd_link)

    sp = sub.add_parser("new", help="Yeni beceri iskeleti olustur")
    sp.add_argument("name")
    sp.add_argument("--applies-to", action="append", help="hangi proje tipleri (bos = hepsi)")
    sp.add_argument("--tag", action="append")
    sp.set_defaults(fn=cmd_new)

    sp = sub.add_parser("list", help="Becerileri ve sicillerini listele")
    sp.add_argument("--project")
    sp.add_argument("--level", choices=LEVELS)
    sp.set_defaults(fn=cmd_list)

    sp = sub.add_parser("context", help="Ajana verilecek brifingi uret (stdout)")
    sp.add_argument("project")
    sp.set_defaults(fn=cmd_context)

    sp = sub.add_parser("log", help="Bir kosunun sonucunu kaydet")
    sp.add_argument("--project", required=True)
    sp.add_argument("--skill", required=True)
    sp.add_argument("--result", required=True, choices=RESULTS)
    sp.add_argument("--autonomous", action="store_true", help="mudahalesiz tamamlandi")
    sp.add_argument("--review-min", type=float, default=0, help="inceleme suren (dk)")
    sp.add_argument("--note")
    sp.set_defaults(fn=cmd_log)

    sp = sub.add_parser("lesson", help="Basarisizliktan cikan kurali kaydet")
    sp.add_argument("--skill", required=True)
    sp.add_argument("--rule", required=True)
    sp.set_defaults(fn=cmd_lesson)

    sp = sub.add_parser("stats", help="Otonomi orani ve inceleme yuku")
    sp.add_argument("--project")
    sp.set_defaults(fn=cmd_stats)

    sp = sub.add_parser("promote", help="Terfi/tenzil adaylarini hesapla")
    sp.add_argument("--apply", action="store_true", help="degisiklikleri yaz")
    sp.add_argument("--verbose", action="store_true")
    sp.set_defaults(fn=cmd_promote)

    sp = sub.add_parser("eval", help="Proje eval setini calistir")
    sp.add_argument("project")
    sp.add_argument("--task", help="tek gorev id (KA-04 gibi)")
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--record", action="store_true", help="sonucu memory/evals altina yaz")
    sp.set_defaults(fn=cmd_eval)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    brain = Brain(brain_home())
    try:
        return args.fn(brain, args)
    except BrainError as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nIptal edildi.", file=sys.stderr)
        return 130
    except OSError as exc:
        print(f"HATA (dosya sistemi): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
