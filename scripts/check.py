#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
subprocess.run(["node", "--test", *map(str, (root / "tests").glob("*.test.js"))], check=True)
subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(root / "tests"), "-p", "test_*.py"], check=True)
for path in (root / "mods").rglob("*.js"):
    subprocess.run(["node", "--check", str(path)], check=True)
home = Path(os.environ.get("HERDR_APP_HOME", Path.home() / ".config/herdr-app"))
mods = [p for p in (root / "mods").iterdir() if p.is_dir()]
mods += [p for p in (home / "mods").glob("pane-rename*") if p.is_dir()]
mods += [home / "mods" / name for name in ["board", "cockpit", "fallout", "lcars", "pasture", "t3-pane", "t3-menu", "win98-dark", "winxp", "evangelion"] if (home / "mods" / name).is_dir()]
if not any(p.name == "pane-rename" for p in mods):
    mods = [p for p in (root / "mods").iterdir() if p.is_dir()]
for mod in mods:
    try:
        subprocess.run(["herdr-app", "check", str(mod)], check=True, timeout=30)
    except subprocess.TimeoutExpired:
        sys.exit(f"Native check timed out for {mod.name}. Run outside the sandbox with macOS GUI-service access.")
status = json.loads(subprocess.check_output(["herdr-app", "status"], timeout=15))
if status.get("errors"):
    sys.exit("Live Herdr errors: " + "; ".join(status["errors"]))
print("Live Herdr status: no errors")
