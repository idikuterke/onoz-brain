"""Gecici kalibrasyon sondasi #2 — KA-01/03/04 davranisini gozlemler.
Kullanim sonrasi silinecek. Tunga'ya yalnizca .godot artifact'i yazdirir.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _probe import probe, GODOT  # noqa: E402

which = sys.argv[1] if len(sys.argv) > 1 else "all"

if which in ("all", "ka01"):
    probe("KA-01 ham kosum", f'"{GODOT}" --headless --path . --quit-after 2 2>&1', timeout=180)

if which in ("all", "checkonly"):
    probe("check-only -s Node scripti",
          f'"{GODOT}" --headless --path . --check-only -s res://tests/test_envanter.gd 2>&1')
    probe("check-only -s olmayan script",
          f'"{GODOT}" --headless --path . --check-only -s res://tests/yok_boyle.gd 2>&1')
    probe("script-only flag var mi",
          f'"{GODOT}" --headless --path . --check-only --script-only 2>&1')

if which in ("all", "suite"):
    probe("test paketi (run_tests.tscn)",
          f'"{GODOT}" --headless --path . res://tests/run_tests.tscn 2>&1', timeout=420)
