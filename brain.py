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
import html
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
    if raw:
        return Path(raw).expanduser().resolve()
    for name in ("onoz-brain", "onozbrain"):
        cand = Path.home() / name
        if (cand / "skills").exists():
            return cand.resolve()
    return (Path.home() / "onoz-brain").resolve()


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
    for s in sorted(skills, key=lambda x: (-LEVELS.index(x["level"]), x["id"])):
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

    print(f"# Proje brifingi: {args.project}")
    print(f"\nProje tipi: {proj['type']} | Etiketler: {', '.join(sorted(ptags))}")
    print(f"Dizin: {proj['path']}\n")

    conv = Path(proj["path"]) / "CONVENTIONS.md"
    if conv.exists():
        try:
            print("## Proje konvansiyonlari\n")
            print(conv.read_text(encoding="utf-8", errors="replace").strip() + "\n")
        except OSError as exc:
            print(f"[uyari] CONVENTIONS.md okunamadi: {exc}", file=sys.stderr)
    else:
        print("## Proje konvansiyonlari\n")
        print("_CONVENTIONS.md yok._ Sifir baglamli bir ajan bu projenin dizin yapisini, "
              "test kalibini ve mimari konvansiyonlarini bilmiyor. "
              "`brain conventions --template > CONVENTIONS.md` ile olustur.\n")

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
            sicil = ("sicil yok (henuz kosulmadi)" if st["total"] == 0 else
                     f"{st['total']} kosu, basari %{st['pass_rate']*100:.0f}, "
                     f"sessiz hata {st['silent']}")
            print(f"- Sicil: {sicil}")
            print(f"- Dosya: {s['_dir']}\n")

    # Ders kayitlari: kapsamsiz olanlar + bu projeye ait olanlar.
    # Baska projeye kapsanmis ders brifinge girmez - gurultu yapar.
    relevant = []
    for l in sorted(brain.lessons_dir.glob("*.md")):
        try:
            body = l.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = re.match(r"<!--\s*project:\s*(.+?)\s*-->", body)
        if m and m.group(1) != args.project:
            continue
        relevant.append(re.sub(r"<!--.*?-->\s*", "", body, count=1).strip())
    if relevant:
        print("## Onceki hatalardan cikan kurallar\n")
        for body in relevant[-15:]:
            print(body + "\n")
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
    header = f"<!-- project: {args.project} -->\n" if args.project else ""
    path.write_text(header + f"- **{args.skill}**: {args.rule}\n", encoding="utf-8")
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


def expand_tokens(cmd: str, brain_root: Path, project_dir: Path) -> str:
    """Platform bagimsiz jeton genisletme. cmd.exe $VAR bilmez, PowerShell %VAR% bilmez."""
    for token in ("$BRAIN_HOME", "${BRAIN_HOME}", "%BRAIN_HOME%"):
        cmd = cmd.replace(token, str(brain_root))
    for token in ("$PROJECT_DIR", "${PROJECT_DIR}", "%PROJECT_DIR%"):
        cmd = cmd.replace(token, str(project_dir))
    return cmd


def assert_tree_safe(project_dir: Path, tasks: list[dict], allow_dirty: bool) -> None:
    """Yikici teardown korumasi.

    setup/teardown iceren gorevler calisma agacini degistirir. Agac kirliyse
    'git checkout -- .' tipi bir teardown commit'lenmemis calismayi siler.
    Bu yuzden kirli agacta mudahaleci gorev kosmayi reddediyoruz.
    """
    invasive = [t for t in tasks if t.get("setup") or t.get("teardown")]
    if not invasive or allow_dirty:
        return
    porcelain = git(project_dir, "status", "--porcelain")
    if porcelain is None:
        print("[uyari] git repo degil veya git yok - agac guvenligi dogrulanamadi.",
              file=sys.stderr)
        return
    dirty = [l for l in porcelain.splitlines() if l.strip()]
    if not dirty:
        return
    # 'git checkout -- .' izlenmeyen dosyaya dokunmaz; 'git clean' dokunur.
    tracked = [d for d in dirty if not d.startswith("??")]
    untracked = [d for d in dirty if d.startswith("??")]
    scripts = " ".join((t.get("setup") or "") + " " + (t.get("teardown") or "")
                       for t in invasive).lower()
    destructive = "git clean" in scripts or "remove-item" in scripts or "rm -rf" in scripts

    risky = tracked if not destructive else dirty
    if not risky:
        if untracked:
            print(f"[bilgi] {len(untracked)} izlenmeyen dosya var; teardown'lar bunlara "
                  f"dokunmuyor, kosuya devam.", file=sys.stderr)
        return

    ornek = "\n  ".join(d[:70] for d in risky[:8])
    more = f"\n  ...{len(risky)-8} dosya daha" if len(risky) > 8 else ""
    ne = "izlenen dosyada degisiklik" if not destructive else "silici teardown + kirli agac"
    raise BrainError(
        f"{ne} ({len(risky)} dosya), {len(invasive)} gorev setup/teardown iceriyor.\n"
        f"Teardown commit'lenmemis calismani silebilir. Once commit veya stash et.\n\n"
        f"  {ornek}{more}\n\n"
        f"Riski biliyorsan: --allow-dirty"
    )


def load_tasks(brain: Brain, project: str) -> list[dict]:
    path = brain.root / "evals" / project / "tasks.jsonl"
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
    for t in tasks:
        try:
            t["timeout"] = int(t.get("timeout", 120))
        except (TypeError, ValueError):
            raise BrainError(f"Gorev {t.get('id','?')}: timeout sayisal olmali, "
                             f"bulunan: {t.get('timeout')!r}")
        t.setdefault("kind", "regression")
    return tasks


def run_shell(cmd: str, brain: Brain, cwd: Path, timeout: int):
    env = dict(os.environ, BRAIN_HOME=str(brain.root))
    return subprocess.run(expand_tokens(cmd, brain.root, cwd), shell=True, cwd=str(cwd),
                          env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def trial_path(brain: Brain, project: str, task_id: str) -> Path:
    return brain.root / "memory" / "trials" / f"{project}__{task_id}.json"


def pending_trials(brain: Brain) -> list[Path]:
    return sorted((brain.root / "memory" / "trials").glob("*.json"))


def record_eval(brain: Brain, project: str, results: list[dict]) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = brain.root / "memory" / "evals" / f"{stamp}-{project}.json"
    passed = sum(1 for r in results if r["ok"])
    write_json(out, {"ts": now_iso(), "project": project, "passed": passed,
                     "total": len(results),
                     "pass_rate": round(passed / (len(results) or 1), 4),
                     "results": results})
    return out


def cmd_trial(brain: Brain, args) -> int:
    """Iki fazli ajan olcumu: setup -> (baska oturum calisir) -> verify.

    Tek komutta setup+verify kosmak ajani aradan cikarir; o olcum daima 0 doner.
    """
    brain.require()
    if args.action == "list":
        pend = pending_trials(brain)
        if not pend:
            print("Bekleyen deneme yok.")
            return 0
        print("BEKLEYEN DENEMELER (agac bozuk durumda, unutma):")
        for f in pend:
            d = read_json(f, default={})
            print(f"  {d.get('project','?')} / {d.get('task','?')}  "
                  f"basladi: {d.get('started','?')}")
        return 0

    proj = brain.project(args.project)
    cwd = Path(proj["path"])
    tasks = [t for t in load_tasks(brain, args.project) if t.get("id") == args.task]
    if not tasks:
        raise BrainError(f"Gorev bulunamadi: {args.task}")
    task = tasks[0]
    if task["kind"] != "agent":
        raise BrainError(f"{args.task} bir ajan gorevi degil (kind={task['kind']}). "
                         f"Regresyon gorevleri icin: brain eval")
    pend = trial_path(brain, args.project, args.task)

    if args.action == "start":
        if pend.exists():
            raise BrainError(f"Bu deneme zaten acik: {pend}\n"
                             f"Bitir: brain trial finish ... | Iptal: brain trial abort ...")
        assert_tree_safe(cwd, [task], args.allow_dirty)
        if task.get("setup"):
            sp = run_shell(task["setup"], brain, cwd, task["timeout"])
            if sp.returncode != 0:
                raise BrainError(f"setup basarisiz (exit={sp.returncode}):\n{sp.stderr[:500]}")
        write_json(pend, {"project": args.project, "task": args.task,
                          "started": now_iso(), "title": task.get("title", "")})
        print(f"DENEME ACILDI: {args.project} / {args.task}")
        print(f"Agac simdi bozuk durumda. Bitirmeden birakma.\n")
        print("--- SIFIR BAGLAMLI OTURUMA VERILECEK ---")
        print(f"1) python brain.py context {args.project}")
        print(f"2) Gorev:\n{task.get('prompt', '(prompt alani bos)')}")
        print("\n--- BITTIGINDE ---")
        print(f"python brain.py trial finish {args.project} {args.task} --record")
        return 0

    if not pend.exists():
        raise BrainError(f"Acik deneme yok: {args.project} / {args.task}\n"
                         f"Once: brain trial start {args.project} {args.task}")

    if args.action == "abort":
        if task.get("teardown"):
            try:
                run_shell(task["teardown"], brain, cwd, task["timeout"])
            except (OSError, subprocess.TimeoutExpired) as exc:
                print(f"[uyari] teardown basarisiz: {exc}", file=sys.stderr)
        pend.unlink()
        print(f"Deneme iptal edildi, agac geri alindi: {args.task}")
        return 0

    # finish
    try:
        proc = run_shell(task["verify"], brain, cwd, task["timeout"])
        ok, detail = proc.returncode == 0, f"exit={proc.returncode}"
        tail = (proc.stdout or proc.stderr or "").strip().splitlines()[-6:]
    except subprocess.TimeoutExpired:
        ok, detail, tail = False, "TIMEOUT", []
    except OSError as exc:
        ok, detail, tail = False, str(exc), []
    finally:
        if task.get("teardown"):
            try:
                run_shell(task["teardown"], brain, cwd, task["timeout"])
            except (OSError, subprocess.TimeoutExpired) as exc:
                print(f"[uyari] teardown basarisiz: {exc}", file=sys.stderr)
        pend.unlink(missing_ok=True)

    print(f"[{'GECTI' if ok else 'KALDI'}] {args.task}  {task.get('title','')}"
          + ("" if ok else f"  ({detail})"))
    for line in tail:
        print("   " + line[:100])
    if args.record:
        out = record_eval(brain, args.project, [{"id": args.task, "ok": ok,
                                                 "detail": detail, "kind": "agent"}])
        print(f"Kaydedildi: {out}")
    else:
        print("Kaydetmek icin: --record")
    return 0 if ok else 1


def cmd_eval(brain: Brain, args) -> int:
    """Sabit gorev setini calistirir. Sistemin butununun olcum aletidir."""
    brain.require()
    proj = brain.project(args.project)
    tasks = load_tasks(brain, args.project)

    if args.task:
        tasks = [t for t in tasks if t.get("id") == args.task]
        if not tasks:
            raise BrainError(f"Gorev bulunamadi: {args.task}")
    if args.kind != "all":
        tasks = [t for t in tasks if t["kind"] == args.kind]
        if not tasks:
            raise BrainError(f"'{args.kind}' turunde gorev yok.")

    cwd = Path(proj["path"])
    if not cwd.exists():
        raise BrainError(f"Proje dizini kayip: {cwd}")

    agent_tasks = [t for t in tasks if t["kind"] == "agent"]
    if agent_tasks and not args.dry_run and not args.selftest:
        raise BrainError(
            f"{len(agent_tasks)} ajan gorevi secildi. 'eval' setup ve verify'i tek komutta "
            f"kosar; ajan aradan cikar ve sonuc DAIMA 0 doner - bu bir olcum degildir.\n\n"
            f"Ajan olcumu iki fazlidir:\n"
            f"  brain trial start {args.project} <GOREV>    # kurar, prompt'u basar\n"
            f"  (sifir baglamli oturum calisir)\n"
            f"  brain trial finish {args.project} <GOREV> --record\n\n"
            f"Gorevin kendisinin saglam olup olmadigini test etmek icin: --selftest")

    if not args.dry_run:
        assert_tree_safe(cwd, tasks, args.allow_dirty)
        if args.selftest and agent_tasks:
            print("SELFTEST modu: gorev saglamligi olculuyor, ajan yetenegi DEGIL.")
            print("Beklenen sonuc: setup sonrasi verify KALMALI.\n")

    env = dict(os.environ, BRAIN_HOME=str(brain.root))
    results = []
    for t in tasks:
        tid, title = t.get("id", "?"), t.get("title", "")
        if args.dry_run:
            flag = " [DUZELTME GEREKIR]" if t.get("needs_adjust") else ""
            print(f"{tid}  {title}{flag}\n      $ {t.get('verify','')}")
            continue
        def sh(cmd, tmo):
            return subprocess.run(expand_tokens(cmd, brain.root, cwd), shell=True,
                                  cwd=str(cwd), env=env, capture_output=True,
                                  text=True, encoding="utf-8", errors="replace",
                                  timeout=tmo)
        try:
            if t.get("setup"):
                sp = sh(t["setup"], t["timeout"])
                if sp.returncode != 0:
                    raise RuntimeError(f"setup basarisiz exit={sp.returncode}")
            proc = sh(t["verify"], t["timeout"])
            ok, detail = proc.returncode == 0, f"exit={proc.returncode}"
        except subprocess.TimeoutExpired:
            ok, detail = False, "TIMEOUT"
        except (OSError, RuntimeError) as exc:
            ok, detail = False, str(exc)
        finally:
            if t.get("teardown"):
                try:
                    sh(t["teardown"], t["timeout"])
                except (OSError, subprocess.TimeoutExpired) as exc:
                    print(f"  [uyari] teardown basarisiz {tid}: {exc}", file=sys.stderr)
        results.append({"id": tid, "ok": ok, "detail": detail, "kind": t["kind"]})
        print(f"[{'GECTI' if ok else 'KALDI'}] {tid}  {title}" + ("" if ok else f"  ({detail})"))

    if args.dry_run:
        print(f"\n{len(tasks)} gorev. Calistirmak icin --dry-run'i kaldir.")
        return 0

    passed = sum(1 for r in results if r["ok"])
    rate = passed / (len(results) or 1)
    print("")
    for kind in ("regression", "agent"):
        grp = [r for r in results if r["kind"] == kind]
        if grp:
            gp = sum(1 for r in grp if r["ok"])
            label = "PROJE SAGLIGI" if kind == "regression" else "AJAN OTONOMISI"
            print(f"{label:<16} {gp}/{len(grp)} = %{gp/len(grp)*100:.1f}")
    print(f"{'TOPLAM':<16} {passed}/{len(results)} = %{rate*100:.1f}")

    if args.record:
        if args.selftest:
            print("SELFTEST sonucu kaydedilmez - otonomi sayisi degil.")
        else:
            print(f"Kaydedildi: {record_eval(brain, args.project, results)}")
    else:
        print("Kaydetmek icin: --record  (baseline'i mutlaka kaydet)")
    return 0 if passed == len(results) else 1


# --------------------------------------------------------------------------
# Durum toplama (otomatik turetilen + STATUS.md)
# --------------------------------------------------------------------------

STATUS_KEYS = ("Durum", "Siradaki", "Engel")


def git(path: Path, *args: str) -> str | None:
    """Git komutu calistirir. Repo degilse / git yoksa None doner, patlamaz."""
    try:
        proc = subprocess.run(["git", "-C", str(path), *args], capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def read_status_md(project_dir: Path) -> dict:
    """Projedeki STATUS.md'den 3 alani okur. Yoksa bos doner - zorunlu degil."""
    out = {k: "" for k in STATUS_KEYS}
    path = project_dir / "STATUS.md"
    if not path.exists():
        return out
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    for line in text.splitlines():
        for key in STATUS_KEYS:
            m = re.match(rf"^\s*[-*]?\s*{key}\s*:\s*(.+)$", line, re.IGNORECASE)
            if m:
                out[key] = m.group(1).strip()
    return out


def latest_evals(brain: Brain, project: str) -> dict:
    """Her kind icin EN SON kaydi ayri dondurur.

    Tek 'son dosya' mantigi yanlisti: ajan kosusu (0/2) regression kaydini (8/10)
    gizliyordu. Dosyalar eskiden yeniye taranir, her kind kendi son degerini alir.
    """
    out: dict[str, dict] = {}
    for f in sorted((brain.root / "memory" / "evals").glob(f"*-{project}.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for kind in ("regression", "agent"):
            grp = [r for r in data.get("results", [])
                   if r.get("kind", "regression") == kind]
            if grp:
                ok = sum(1 for r in grp if r.get("ok"))
                out[kind] = {"passed": ok, "total": len(grp),
                             "rate": ok / len(grp), "ts": data.get("ts", "")}
    return out


def collect_status(brain: Brain) -> list[dict]:
    rows = []
    for name, meta in sorted(brain.projects().items()):
        path = Path(meta["path"])
        row = {"name": name, "type": meta.get("type", "?"), "path": str(path),
               "exists": path.exists(), "branch": "-", "last_commit": "-",
               "days": None, "dirty": None, "commits_30d": None,
               "evals": {}, "runs": len(brain.runs(project=name))}
        if path.exists():
            row["branch"] = git(path, "rev-parse", "--abbrev-ref", "HEAD") or "-"
            iso = git(path, "log", "-1", "--format=%cI")
            if iso:
                row["days"] = days_since(iso)
                row["last_commit"] = (git(path, "log", "-1", "--format=%s") or "")[:60]
            porcelain = git(path, "status", "--porcelain")
            if porcelain is not None:
                row["dirty"] = len([l for l in porcelain.splitlines() if l.strip()])
            recent = git(path, "log", "--since=30.days", "--format=%h")
            if recent is not None:
                row["commits_30d"] = len([l for l in recent.splitlines() if l.strip()])
            row.update(read_status_md(path))
        row["evals"] = latest_evals(brain, name)
        rows.append(row)
    return rows


STATUS_TEMPLATE = """# Durum

Durum: <tek cumle - proje su an nerede>
Siradaki: <tek cumle - bir sonraki somut adim>
Engel: <varsa tek cumle, yoksa bos birak>

<!-- Uc satir. Daha fazlasi yazma; bu dosya gorev takipcisi degil,
     panoda gorunecek ozet. Degistiginde guncelle, haftalik ritual yapma. -->
"""


CONVENTIONS_TEMPLATE = """# Konvansiyonlar

> Sifir baglamli bir ajanin bu projede calisabilmesi icin bilmesi gerekenler.
> Gorev metinleri sabit kalir; ogrenme BU dosyada birikir.
> Cozumu degil, kurali yaz. "X hatasi su satirda" degil, "hatalar su kalipla aranir".

## Dizin yapisi

- `scripts/` — ...
- `scenes/` — ...
- `tests/` — ...

## Test kalibi

- Suit girisi: `res://tests/run_tests.gd`, cikis kodu 0/1
- Her test dosyasi: `extends Node`, `calistir() -> Array[Dictionary]`, `_kaydet` kalibi
- Yeni test keşfi: <suit yeni dosyayi nasil buluyor>
- Ornek dosyalar: `tests/test_etkilesim.gd`, `tests/test_boss.gd`

## Mimari konvansiyonlar

- Sinyal/olay: <EventBus var mi, adlandirma kurali>
- Autoload'lar: <hangileri, ne ise yarar>
- Isimlendirme: <Turkce mi Ingilizce mi, snake_case mi>

## Bilinen tuzaklar

- <ajanin duseceği, belgelenmemis seyler>
"""


def cmd_conventions(brain: Brain, args) -> int:
    print(CONVENTIONS_TEMPLATE)
    return 0


def cmd_status(brain: Brain, args) -> int:
    if args.template:
        print(STATUS_TEMPLATE)
        return 0
    brain.require()
    rows = collect_status(brain)
    if not rows:
        print("Kayitli proje yok. 'brain link' ile ekle.")
        return 0
    print(f"{'PROJE':<18}{'TIP':<13}{'DAL':<12}{'SON':>5}{'KIRLI':>7}{'30G':>5}"
          f"{'SAGLIK':>8}{'OTONOMI':>9}")
    print("-" * 82)
    for r in rows:
        if not r["exists"]:
            print(f"{r['name']:<18}{'DIZIN YOK':<13}{r['path'][:40]}")
            continue
        ev = r["evals"]
        reg = f"%{ev['regression']['rate']*100:.0f}" if "regression" in ev else "-"
        agt = f"%{ev['agent']['rate']*100:.0f}" if "agent" in ev else "-"
        days = f"{r['days']}g" if r["days"] is not None else "-"
        print(f"{r['name']:<18}{r['type']:<13}{r['branch'][:11]:<12}{days:>5}"
              f"{('-' if r['dirty'] is None else r['dirty']):>7}"
              f"{('-' if r['commits_30d'] is None else r['commits_30d']):>5}"
              f"{reg:>8}{agt:>9}")
        nxt = r.get("Siradaki", "")
        blk = r.get("Engel", "")
        if nxt:
            print(f"{'':<18}-> {nxt[:80]}")
        if blk:
            print(f"{'':<18}!! ENGEL: {blk[:80]}")
    pend = pending_trials(brain)
    if pend:
        print(f"\n!! {len(pend)} ACIK DENEME - ilgili agac bozuk durumda:")
        for f in pend:
            d = read_json(f, default={})
            print(f"   {d.get('project','?')} / {d.get('task','?')}  "
                  f"-> brain trial finish|abort")

    missing = [r["name"] for r in rows if r["exists"] and not r.get("Siradaki")]
    if missing:
        print(f"\nSTATUS.md eksik/bos: {', '.join(missing)}")
        print("Sablon: brain status --template > <proje>/STATUS.md")
    return 0


DASH_CSS = """
*{box-sizing:border-box}body{margin:0;padding:24px;background:#12131a;color:#e6e6ea;
font:14px/1.5 ui-sans-serif,system-ui,Segoe UI,sans-serif}
h1{font-size:20px;margin:0 0 4px}.sub{color:#8b8f9e;font-size:13px;margin-bottom:20px}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.card{background:#1b1d26;border:1px solid #2a2d3a;border-radius:10px;padding:14px}
.card.warn{border-color:#7a5c1f}.card.err{border-color:#8a2f2f}
.name{font-weight:600;font-size:15px}.type{color:#8b8f9e;font-size:12px;margin-left:6px}
.m{display:flex;gap:14px;margin:10px 0;flex-wrap:wrap}
.m div{font-size:12px;color:#8b8f9e}.m b{display:block;color:#e6e6ea;font-size:16px;font-weight:600}
.next{margin-top:8px;padding:8px;background:#22252f;border-radius:6px;font-size:13px}
.blk{margin-top:6px;padding:8px;background:#3a2020;border-radius:6px;font-size:13px}
.none{color:#6b6f7e;font-style:italic;font-size:12px;margin-top:8px}
h2{font-size:17px;margin:28px 0 6px}h3{font-size:13px;color:#8b8f9e;margin:18px 0 6px;font-weight:500}
.chips{margin-bottom:8px}.chip{display:inline-block;background:#22252f;border:1px solid #2a2d3a;
border-radius:20px;padding:2px 10px;font-size:12px;margin:0 6px 6px 0;color:#b8bcc8}
ul.log{list-style:none;margin:8px 0 0;padding:0}
ul.log li{font-size:12.5px;padding:3px 0;border-top:1px solid #22252f;color:#c8ccd6}
ul.log li .k{display:inline-block;min-width:66px;color:#6f8f7a;font-size:11px}
.bar{height:5px;background:#2a2d3a;border-radius:3px;overflow:hidden;margin-top:10px}
.bar i{display:block;height:100%;background:#4a8f5c}
footer{margin-top:24px;color:#6b6f7e;font-size:12px}
"""


def render_activity(commits: list[dict], days: int) -> str:
    if not commits:
        return (f'<h2>Son {days} gun</h2>'
                f'<div class="none">Commit bulunamadi.</div>')
    e = html.escape
    by_project: dict[str, list] = {}
    by_kind: dict[str, int] = {}
    for c in commits:
        by_project.setdefault(c["project"], []).append(c)
        by_kind[c["kind"]] = by_kind.get(c["kind"], 0) + 1
    chips = " ".join(f'<span class="chip">{e(k)} {v}</span>' for k, v in
                     sorted(by_kind.items(), key=lambda x: -x[1]))
    blocks = []
    for proj, items in sorted(by_project.items(), key=lambda x: -len(x[1])):
        lis = "".join(f'<li><span class="k">{e(c["kind"])}</span>{e(c["subject"][:90])}</li>'
                      for c in items[:8])
        more = (f'<li class="none">...{len(items)-8} commit daha</li>'
                if len(items) > 8 else "")
        blocks.append(f'<div class="card"><div class="name">{e(proj)}'
                      f'<span class="type">{len(items)} commit</span></div>'
                      f'<ul class="log">{lis}{more}</ul></div>')
    return (f'<h2>Son {days} gun &middot; {len(by_project)} proje &middot; '
            f'{len(commits)} commit</h2><div class="chips">{chips}</div>'
            f'<h3>Haftalik commit</h3>{svg_weekly(commits)}'
            f'<div class="grid">{"".join(blocks)}</div>'
            f'<div class="none">Commit sayisi is hacminin zayif olcusudur; '
            f'asil bilgi basliklardir.</div>')


def render_dashboard(rows: list[dict], generated: str,
                     commits: list[dict] | None = None, days: int = 7) -> str:
    e = html.escape
    cards = []
    for r in rows:
        if not r["exists"]:
            cards.append(f'<div class="card err"><div class="name">{e(r["name"])}</div>'
                         f'<div class="none">Dizin bulunamadi: {e(r["path"])}</div></div>')
            continue
        cls = "card"
        if r.get("Engel"):
            cls = "card err"
        elif r["days"] is not None and r["days"] > 30:
            cls = "card warn"
        ev = r["evals"]
        reg = ev.get("regression")
        agt = ev.get("agent")
        reg_txt = f'%{reg["rate"]*100:.0f}' if reg else "-"
        agt_txt = f'%{agt["rate"]*100:.0f}' if agt else "-"
        bar = (f'<div class="bar"><i style="width:{reg["rate"]*100:.0f}%"></i></div>'
               if reg else "")
        parts = [f'<div class="{cls}">',
                 f'<div><span class="name">{e(r["name"])}</span>'
                 f'<span class="type">{e(r["type"])}</span></div>',
                 '<div class="m">',
                 f'<div>son commit<b>{r["days"] if r["days"] is not None else "-"}g</b></div>',
                 f'<div>30 gun<b>{r["commits_30d"] if r["commits_30d"] is not None else "-"}</b></div>',
                 f'<div>kirli<b>{r["dirty"] if r["dirty"] is not None else "-"}</b></div>',
                 f'<div>saglik<b>{reg_txt}</b></div>',
                 f'<div>otonomi<b>{agt_txt}</b></div>',
                 f'<div>kosu<b>{r["runs"]}</b></div>',
                 '</div>', bar]
        if r.get("Durum"):
            parts.append(f'<div class="next">{e(r["Durum"])}</div>')
        if r.get("Siradaki"):
            parts.append(f'<div class="next">-> {e(r["Siradaki"])}</div>')
        if r.get("Engel"):
            parts.append(f'<div class="blk">ENGEL: {e(r["Engel"])}</div>')
        if not any(r.get(k) for k in STATUS_KEYS):
            parts.append('<div class="none">STATUS.md yok - durum bilgisi elle girilir</div>')
        parts.append("</div>")
        cards.append("".join(parts))

    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>ONOZ Brain</title><style>{DASH_CSS}</style></head><body>'
            f'<h1>Proje panosu</h1>'
            f'<div class="sub">{len(rows)} proje &middot; uretim: {e(generated)} '
            f'&middot; salt okunur, veri girisi STATUS.md ve git uzerinden</div>'
            f'<div class="grid">{"".join(cards)}</div>'
            f'{render_activity(commits or [], days)}'
            f'<footer>Sari kart: 30+ gun commit yok. Kirmizi: engel var veya dizin kayip. '
            f'Bunlar etkinlik sinyalidir, yargi degil.</footer></body></html>')


def cmd_dashboard(brain: Brain, args) -> int:
    brain.require()
    rows = collect_status(brain)
    commits = collect_activity(brain, args.days, args.exclude)
    out = Path(args.out) if args.out else brain.root / "memory" / "dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_dashboard(rows, now_iso(), commits, args.days), encoding="utf-8")
    print(f"Pano yazildi: {out}")
    if args.open:
        import webbrowser
        webbrowser.open(out.resolve().as_uri())
    return 0


# --------------------------------------------------------------------------
# Etkinlik: commit mesajlarindan anlamli ozet
# --------------------------------------------------------------------------

KIND_KEYWORDS = [
    ("asset",    ("asset", "sprite", "texture", "atlas", "mesh", "model", "ses", "muzik",
                  "müzik", "gorsel", "görsel", "ikon", "shader", "animasyon")),
    ("test",     ("test", "testi", "testler", "eval", "spec", "coverage")),
    ("dokuman",  ("docs", "doc", "readme", "belge", "dokuman", "doküman", "yorum", "changelog")),
    ("duzeltme", ("fix", "bug", "hata", "duzelt", "düzelt", "duzeltildi", "düzeltildi",
                  "onar", "onarildi", "onarıldı", "patch", "hotfix")),
    ("refactor", ("refactor", "cleanup", "temizle", "temizlik", "sadelestir", "sadeleştir",
                  "yeniden", "tasindi", "taşındı", "bolundu", "bölündü")),
    ("bakim",    ("chore", "bump", "deps", "bagimlilik", "bağımlılık", "config", "ci",
                  "build", "versiyon", "surum", "sürüm", "pipeline")),
    ("ozellik",  ("feat", "add", "ekle", "eklendi", "yeni", "implement", "olustur",
                  "oluştur", "uygulandi", "uygulandı")),
]
CONV_RE = re.compile(r"^(feat|fix|refactor|test|docs|chore|perf|style|build|ci)\b", re.I)
CONV_MAP = {"feat": "ozellik", "fix": "duzeltme", "refactor": "refactor", "test": "test",
            "docs": "dokuman", "chore": "bakim", "perf": "refactor", "style": "refactor",
            "build": "bakim", "ci": "bakim"}


def classify(subject: str) -> str:
    m = CONV_RE.match(subject.strip())
    if m:
        return CONV_MAP.get(m.group(1).lower(), "diger")
    tokens = set(re.findall(r"\w+", subject.lower(), re.UNICODE))
    for kind, words in KIND_KEYWORDS:
        if tokens & set(words):
            return kind
    return "diger"


def collect_activity(brain: Brain, days: int, exclude: list[str] | None = None) -> list[dict]:
    """Bagli tum projelerin commit gecmisini toplar. Merge commit'leri disarida."""
    commits = []
    for name, meta in sorted(brain.projects().items()):
        if name in (exclude or ()):
            continue
        path = Path(meta["path"])
        if not path.exists():
            continue
        raw = git(path, "log", "--no-merges", f"--since={days}.days",
                  "--format=%h\x1f%cI\x1f%s")
        if not raw:
            continue
        for line in raw.splitlines():
            parts = line.split("\x1f")
            if len(parts) != 3:
                continue
            sha, iso, subject = parts
            commits.append({"project": name, "type": meta.get("type", "?"), "sha": sha,
                            "iso": iso, "subject": subject.strip(),
                            "kind": classify(subject)})
    return commits


def week_key(iso: str) -> str:
    try:
        d = datetime.fromisoformat(iso)
    except ValueError:
        return "?"
    y, w, _ = d.isocalendar()
    return f"{y}-H{w:02d}"


def cmd_activity(brain: Brain, args) -> int:
    brain.require()
    commits = collect_activity(brain, args.days, args.exclude)
    if not commits:
        print(f"Son {args.days} gunde commit yok (veya projeler git reposu degil).")
        return 0

    by_project: dict[str, list] = {}
    by_kind: dict[str, int] = {}
    for c in commits:
        by_project.setdefault(c["project"], []).append(c)
        by_kind[c["kind"]] = by_kind.get(c["kind"], 0) + 1

    if args.md:
        print(f"## Son {args.days} gun — {len(by_project)} proje, {len(commits)} commit\n")
        for proj, items in sorted(by_project.items(), key=lambda x: -len(x[1])):
            print(f"### {proj} ({len(items)})")
            for c in items[:args.limit]:
                print(f"- `{c['kind']}` {c['subject']}")
            if len(items) > args.limit:
                print(f"- _...{len(items)-args.limit} commit daha_")
            print()
        print("**Basliklar:** " + ", ".join(f"{k} {v}" for k, v in
              sorted(by_kind.items(), key=lambda x: -x[1])))
        return 0

    print(f"SON {args.days} GUN — {len(by_project)} proje, {len(commits)} commit\n")
    for proj, items in sorted(by_project.items(), key=lambda x: -len(x[1])):
        print(f"{proj} ({items[0]['type']}) — {len(items)} commit")
        for c in items[:args.limit]:
            print(f"   {c['kind']:<9} {c['subject'][:66]}")
        if len(items) > args.limit:
            print(f"   {'':<9} ...{len(items)-args.limit} commit daha")
        print()
    print("BASLIKLAR: " + "  ".join(f"{k}={v}" for k, v in
          sorted(by_kind.items(), key=lambda x: -x[1])))
    print("\nNot: commit sayisi is hacminin zayif olcusudur. Tek commit bir haftalik "
          "is olabilir; asil bilgi yukaridaki basliklardir.")
    return 0


def svg_weekly(commits: list[dict], weeks: int = 8) -> str:
    """Bagimliliksiz SVG sutun grafik: son N haftanin commit sayisi."""
    buckets: dict[str, int] = {}
    for c in commits:
        buckets[week_key(c["iso"])] = buckets.get(week_key(c["iso"]), 0) + 1
    keys = sorted(buckets)[-weeks:]
    if not keys:
        return '<div class="none">Grafik icin yeterli veri yok</div>'
    vals = [buckets[k] for k in keys]
    top = max(vals) or 1
    w, h, pad = 100.0 / len(keys), 90, 0.18
    bars = []
    for i, (k, v) in enumerate(zip(keys, vals)):
        bh = (v / top) * (h - 22)
        x, bw = i * w + w * pad, w * (1 - 2 * pad)
        bars.append(
            f'<rect x="{x:.2f}%" y="{h-14-bh:.1f}" width="{bw:.2f}%" height="{bh:.1f}" '
            f'rx="2" fill="#4a8f5c"/>'
            f'<text x="{x+bw/2:.2f}%" y="{h-16-bh:.1f}" fill="#8b8f9e" font-size="9" '
            f'text-anchor="middle">{v}</text>'
            f'<text x="{x+bw/2:.2f}%" y="{h-3}" fill="#6b6f7e" font-size="8" '
            f'text-anchor="middle">{html.escape(k.split("-")[1])}</text>')
    return f'<svg viewBox="0 0 100 {h}" preserveAspectRatio="none" style="width:100%;height:{h}px">{"".join(bars)}</svg>'


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
    sp.add_argument("--project", help="dersi tek projeye kapsa (bos = tum projeler)")
    sp.set_defaults(fn=cmd_lesson)

    sp = sub.add_parser("stats", help="Otonomi orani ve inceleme yuku")
    sp.add_argument("--project")
    sp.set_defaults(fn=cmd_stats)

    sp = sub.add_parser("promote", help="Terfi/tenzil adaylarini hesapla")
    sp.add_argument("--apply", action="store_true", help="degisiklikleri yaz")
    sp.add_argument("--verbose", action="store_true")
    sp.set_defaults(fn=cmd_promote)

    sp = sub.add_parser("status", help="Tum projelerin tek ekran ozeti")
    sp.add_argument("--template", action="store_true", help="STATUS.md sablonunu bas")
    sp.set_defaults(fn=cmd_status)

    sp = sub.add_parser("activity", help="Commit mesajlarindan donem ozeti")
    sp.add_argument("--days", type=int, default=7)
    sp.add_argument("--limit", type=int, default=8, help="proje basina gosterilecek commit")
    sp.add_argument("--md", action="store_true", help="markdown cikti (rapora yapistirmalik)")
    sp.add_argument("--exclude", action="append",
                    help="projeyi disarida birak (otomatik commit ureten projeler icin)")
    sp.set_defaults(fn=cmd_activity)

    sp = sub.add_parser("conventions", help="CONVENTIONS.md sablonunu bas")
    sp.add_argument("--template", action="store_true")
    sp.set_defaults(fn=cmd_conventions)

    sp = sub.add_parser("dashboard", help="Tarayici panosu uret (tek dosya HTML)")
    sp.add_argument("--out", help="cikti yolu")
    sp.add_argument("--open", action="store_true", help="tarayicida ac")
    sp.add_argument("--days", type=int, default=7, help="etkinlik penceresi")
    sp.add_argument("--exclude", action="append", help="projeyi disarida birak")
    sp.set_defaults(fn=cmd_dashboard)

    sp = sub.add_parser("eval", help="Proje eval setini calistir")
    sp.add_argument("project")
    sp.add_argument("--task", help="tek gorev id (KA-04 gibi)")
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--record", action="store_true", help="sonucu memory/evals altina yaz")
    sp.add_argument("--kind", choices=["all", "regression", "agent"], default="all")
    sp.add_argument("--allow-dirty", action="store_true",
                    help="kirli agacta mudahaleci gorev kosmaya izin ver (riskli)")
    sp.add_argument("--selftest", action="store_true",
                    help="ajan gorevinin saglamligini olc (setup sonrasi verify KALMALI)")
    sp.set_defaults(fn=cmd_eval)

    sp = sub.add_parser("trial", help="Iki fazli ajan olcumu (start/finish/abort/list)")
    sp.add_argument("action", choices=["start", "finish", "abort", "list"])
    sp.add_argument("project", nargs="?")
    sp.add_argument("task", nargs="?")
    sp.add_argument("--record", action="store_true")
    sp.add_argument("--allow-dirty", action="store_true")
    sp.set_defaults(fn=cmd_trial)

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
