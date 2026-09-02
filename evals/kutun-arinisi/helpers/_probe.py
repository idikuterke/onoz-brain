"""Geçici kalibrasyon sondası — brain.py cmd_eval'in subprocess davranisini taklit eder.
Kullanim sonrasi silinecek. BRAIN_HOME'a yazilan tek sey budur (kalibrasyon sinirlari icinde).
"""
import os
import subprocess
import sys

TUNGA = r"C:\Users\pc\Tunga"
GODOT = r"C:\Godot\Godot_v4.7.1-stable_win64_console.exe"


def run(verify, cwd=TUNGA, timeout=180):
    """brain.py cmd_eval'in birebir kopyasi (satir 536-539)."""
    env = dict(os.environ, BRAIN_HOME=r"C:\Users\pc\onozbrain")
    try:
        proc = subprocess.run(verify, shell=True, cwd=str(cwd), env=env,
                              capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "", ""


def probe(name, verify, cwd=TUNGA, timeout=180):
    code, out, err = run(verify, cwd=cwd, timeout=timeout)
    print(f"--- {name}: exit={code}")
    if out:
        print("STDOUT (ilk 600):", out[:600])
    if err:
        print("STDERR (ilk 600):", err[:600])
    return code, out, err


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"

    if which in ("all", "env"):
        probe("BRAIN_HOME genislemesi", "echo %BRAIN_HOME%")
        probe("python cozumleme", "python --version")
        probe("godot dogrudan yol", f'"{GODOT}" --version')

    if which in ("all", "ka01"):
        # KA-01 benzeri: headless acilis, ciktiya bak
        probe("KA-01 ham kosum",
              f'"{GODOT}" --headless --path . --quit-after 2 2>&1')

    if which in ("all", "abs"):
        # -s ile absolute path destekleniyor mu
        probe("-s absolute path",
              f'"{GODOT}" --headless --path . -s "C:/Users/pc/onozbrain/evals/kutun-arinisi/helpers/probe_tree.gd"')
