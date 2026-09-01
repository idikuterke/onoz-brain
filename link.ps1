# Projeleri toplu bagla (Windows). YOLLARI DUZELT, sonra calistir.
$ErrorActionPreference = "Stop"
$Brain = "$env:BRAIN_HOME\brain.py"
$P = "$env:USERPROFILE\projects"   # <-- kok dizinini duzelt

$projects = @(
  @{n="kutun-arinisi";   d="kutun-arinisi";   t="godot";       tags=@("gdscript","rpg")},
  @{n="onoz-idle";       d="onoz-idle";       t="godot";       tags=@("idle","mobile")},
  @{n="gokyazi";         d="gokyazi";         t="flutter";     tags=@("dart","mobile")},
  @{n="gokyuzu-gunlugu"; d="gokyuzu-gunlugu"; t="flutter";     tags=@("dart","offline")},
  @{n="onoz-web";        d="onoz-web";        t="web";         tags=@("nextjs","ts")},
  @{n="gokturk-studio";  d="gokturk-studio";  t="python-tool"; tags=@("ml","cv")},
  @{n="gokturk-font";    d="gokturk-font";    t="python-tool"; tags=@("fonttools")},
  @{n="gokturk-klavye";  d="gokturk-klavye";  t="web";         tags=@("static")},
  @{n="rota";            d="rota";            t="flutter";     tags=@("dart")},
  @{n="dil-oyunu";       d="dil-oyunu";       t="web";         tags=@("game")},
  @{n="career-ops";      d="career-ops";      t="python-tool"; tags=@("automation")}
)

foreach ($p in $projects) {
  $path = Join-Path $P $p.d
  if (-not (Test-Path $path)) { Write-Warning "Atlandi (dizin yok): $path"; continue }
  $args = @("link", $p.n, $path, "--type", $p.t)
  foreach ($t in $p.tags) { $args += @("--tag", $t) }
  python $Brain @args
}
python $Brain list
