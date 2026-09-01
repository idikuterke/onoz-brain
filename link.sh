#!/usr/bin/env bash
# Projeleri toplu bagla. YOLLARI KENDI MAKINENE GORE DUZELT, sonra calistir.
set -euo pipefail
BRAIN="python ${BRAIN_HOME:-$HOME/onoz-brain}/brain.py"
P="$HOME/projects"   # <-- kok dizinini duzelt

$BRAIN link kutun-arinisi   "$P/kutun-arinisi"   --type godot       --tag gdscript --tag rpg
$BRAIN link onoz-idle       "$P/onoz-idle"       --type godot       --tag idle --tag mobile
$BRAIN link gokyazi         "$P/gokyazi"         --type flutter     --tag dart --tag mobile
$BRAIN link gokyuzu-gunlugu "$P/gokyuzu-gunlugu" --type flutter     --tag dart --tag offline
$BRAIN link onoz-web        "$P/onoz-web"        --type web         --tag nextjs --tag ts
$BRAIN link gokturk-studio  "$P/gokturk-studio"  --type python-tool --tag ml --tag cv
$BRAIN link gokturk-font    "$P/gokturk-font"    --type python-tool --tag fonttools
$BRAIN link gokturk-klavye  "$P/gokturk-klavye"  --type web         --tag static
$BRAIN link rota            "$P/rota"            --type flutter     --tag dart
$BRAIN link dil-oyunu       "$P/dil-oyunu"       --type web         --tag game
$BRAIN link career-ops      "$P/career-ops"      --type python-tool --tag automation

$BRAIN list
