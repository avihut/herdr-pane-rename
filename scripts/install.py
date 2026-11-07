#!/usr/bin/env python3
"""Plan first, back up, then apply guarded layout integrations. No network access."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from adapters import adapt, adapt_layout

ROOT = Path(__file__).resolve().parents[1]
BUILTINS = {"main", "terminals", "win98"}
# These sources have active owners. Integration is an owner-reviewed source patch.
DEFERRED = {"winxp", "evangelion", "fallout"}
ADAPTERS = {
    "t3-pane": ["main.js"], "t3-menu": ["main.js"], "board": ["main.js"],
    "pasture": ["main.js"], "fallout": ["main.js"], "lcars": ["main.js"],
    "cockpit": ["pane.js"], "win98-dark": ["window.js", "kit.js"],
}
CLONES = {"pane": "pane-rename-herdr", "terminals-pane": "pane-rename-terminals"}

def encoded(doc):
    return (json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def plan(home):
    writes, originals, clones = {}, {}, {}
    def add(rel, data):
        old = (home / rel).read_bytes() if (home / rel).is_file() else None
        if old != data:
            writes[rel], originals[rel] = data, old

    for path in (ROOT / "mods").rglob("*"):
        if path.is_file() and path.name not in {"gpui-kit.d.ts", "jsconfig.json"}:
            rel = str(path.relative_to(ROOT))
            if (home / rel).exists() and (home / rel).read_bytes() != path.read_bytes():
                raise ValueError(f"Mod name collision at {rel}; refusing to overwrite")
            add(rel, path.read_bytes())
    layouts = []
    used = set()
    for path in sorted((home / "layouts").glob("*.json")):
        # XP is being developed independently; use the source-patch task for it.
        if path.stem in BUILTINS | DEFERRED:
            continue
        doc = json.loads(path.read_text())
        def scan(node):
            if isinstance(node, dict):
                content = node.get("content", {})
                if "mod" in content:
                    used.add(content["mod"])
                header_mod = content.get("pane", {}).get("header", {}).get("content", {}).get("mod")
                supported = set(ADAPTERS) | set(CLONES) | {"pane-rename-header"}
                if header_mod and header_mod not in supported:
                    raise ValueError(f"Layout {path.stem} has an unadapted header: {header_mod}; add an adapter first")
                for value in node.values(): scan(value)
            elif isinstance(node, list):
                for value in node: scan(value)
        scan(doc)
        add(str(path.relative_to(home)), encoded(adapt_layout(doc, path.stem)))
        layouts.append(path.stem)
    for mod, files in ADAPTERS.items():
        if mod not in used and mod != "t3-menu":
            continue
        for file in files:
            rel = f"mods/{mod}/{file}"
            if (home / rel).is_file():
                add(rel, adapt(f"{mod}/{file}", (home / rel).read_text()).encode())
    for source, target in CLONES.items():
        if source not in used:
            continue
        if (home / "mods" / target).exists():
            raise ValueError(f"Clone name already exists: {target}")
        clones[source] = target
        for path in (home / "mods" / source).rglob("*"):
            if not path.is_file() or path.name in {"jsconfig.json"} or path.suffix == ".ts":
                continue
            rel = f"mods/{target}/{path.relative_to(home / 'mods' / source)}"
            data = path.read_bytes()
            if path.name == "main.js":
                data = adapt(f"{source}/main.js", path.read_text()).encode()
            add(rel, data)
    keys_path = home / "keys.json"
    keys = json.loads(keys_path.read_text()) if keys_path.exists() else {}
    shortcut = "cmd-f2" if sys.platform == "darwin" else "ctrl-shift-f2"
    action = "mod.open:pane-rename"
    for section, bindings in keys.items():
        if shortcut in bindings and bindings[shortcut] != action:
            raise ValueError(f"Shortcut conflict in {section}: {shortcut}; choose a free shortcut first")
    keys.setdefault("global", {})[shortcut] = action
    add("keys.json", encoded(keys))
    return writes, originals, clones, layouts

def write_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".pane-rename-tmp")
    temp.write_bytes(data)
    temp.replace(path)

def uninstall(home):
    backup = home / ".pane-rename-backup"
    manifest = json.loads((backup / "manifest.json").read_text())
    applied = {rel: item for rel, item in manifest.items() if item.get("applied", True)}
    conflicts = [rel for rel, item in applied.items()
                 if not (home / rel).is_file() or digest((home / rel).read_bytes()) != item["installed"]]
    if conflicts:
        raise ValueError("Files changed since installation; preserving all files: " + ", ".join(conflicts))
    for rel, item in applied.items():
        if item["existed"]:
            write_atomic(home / rel, (backup / rel).read_bytes())
        else:
            (home / rel).unlink()
    # Empty mod directories are safe to remove; unknown files remain.
    directories = set()
    for rel in applied:
        if rel.startswith("mods/"):
            parent = (home / rel).parent
            while parent != home / "mods":
                directories.add(parent)
                parent = parent.parent
    for directory in sorted(directories, key=lambda p: len(p.parts), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()): directory.rmdir()
    shutil.rmtree(backup)
    print("Restored all pre-installation files; saved pane names remain in shared state.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", type=Path, default=Path(os.environ.get("HERDR_APP_HOME", Path.home() / ".config/herdr-app")))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stage", type=Path, help="Write review files to a separate directory only")
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()
    if args.uninstall:
        uninstall(args.home); return
    if (args.home / ".pane-rename-backup").exists():
        raise ValueError("An installation backup already exists; uninstall before reinstalling")
    writes, originals, clones, layouts = plan(args.home)
    print(json.dumps({"layouts": layouts, "deferred": sorted(DEFERRED), "clones": clones, "files": sorted(writes)}, indent=2))
    if args.dry_run: return
    if args.stage:
        for rel, data in sorted(writes.items(), key=lambda item: (not item[0].endswith("mod.json"), item[0])):
            write_atomic(args.stage / rel, data)
        (args.stage / "plan.json").write_bytes(encoded({"layouts": layouts, "files": sorted(writes)}))
        return
    backup = args.home / ".pane-rename-backup"
    # Recheck every original before making changes, including files another agent could edit.
    for rel, original in originals.items():
        current = (args.home / rel).read_bytes() if (args.home / rel).is_file() else None
        if current != original: raise ValueError(f"Concurrent edit: {rel}")
    # Check communication before any writes, so socket failures leave no partial install.
    env = dict(os.environ, HERDR_APP_HOME=str(args.home))
    subprocess.run(["herdr-app", "status"], env=env, check=True, capture_output=True, timeout=15)
    backup.mkdir()
    manifest = {}
    for rel, data in writes.items():
        old = originals[rel]
        if old is not None: write_atomic(backup / rel, old)
        manifest[rel] = {"installed": digest(data), "existed": old is not None, "applied": False}
    write_atomic(backup / "manifest.json", encoded(manifest))
    # Clone Herdr-owned headers through the app, never edit the originals.
    for source, target in clones.items():
        subprocess.run(["herdr-app", "do", "mod.clone", json.dumps({"name": source, "as": target})], env=env, check=True)
        for path in (args.home / "mods" / target).rglob("*"):
            if path.is_file():
                rel = str(path.relative_to(args.home))
                manifest[rel] = {"installed": digest(path.read_bytes()), "existed": False, "applied": True}
        # Retain the app-generated clone provenance instead of copying the shipped manifest back.
        rel = f"mods/{target}/mod.json"
        writes[rel] = (args.home / rel).read_bytes()
        manifest[rel]["installed"] = digest(writes[rel])
        write_atomic(backup / "manifest.json", encoded(manifest))
    published_mods = set()
    for rel, data in sorted(writes.items(), key=lambda item: (not item[0].endswith("mod.json"), item[0])):
        if rel.startswith("mods/pane-rename") and Path(rel).parts[1] in published_mods:
            continue
        current = (args.home / rel).read_bytes() if (args.home / rel).is_file() else None
        expected = manifest[rel]["installed"] if manifest[rel]["applied"] else (digest(originals[rel]) if originals[rel] is not None else None)
        if (digest(current) if current is not None else None) != expected:
            raise ValueError(f"Concurrent edit while installing: {rel}; run uninstall to restore already-applied files")
        if rel.startswith("mods/pane-rename"):
            # Publish each complete owned mod once. Per-file writes reload the host VM
            # repeatedly and can exhaust it on a large active layout.
            mod_dir = Path(rel).parts[1]
            if mod_dir in published_mods:
                continue
            members = {r: d for r, d in writes.items() if r.startswith(f"mods/{mod_dir}/")}
            stage = backup / ".staging" / mod_dir
            target = args.home / "mods" / mod_dir
            previous = backup / ".staging" / (mod_dir + ".previous")
            if target.exists(): shutil.copytree(target, stage)
            else: stage.mkdir(parents=True)
            for member, content in sorted(members.items(), key=lambda item: not item[0].endswith("mod.json")):
                write_atomic(stage / Path(member).relative_to(f"mods/{mod_dir}"), content)
            for member in members:
                current_bytes = (args.home / member).read_bytes() if (args.home / member).is_file() else None
                expected_hash = manifest[member]["installed"] if manifest[member]["applied"] else (digest(originals[member]) if originals[member] is not None else None)
                if (digest(current_bytes) if current_bytes is not None else None) != expected_hash:
                    raise ValueError(f"Concurrent edit while staging: {member}")
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists(): target.rename(previous)
            try: stage.rename(target)
            except OSError:
                if previous.exists(): previous.rename(target)
                raise
            for member, content in members.items():
                manifest[member].update(installed=digest(content), applied=True)
            write_atomic(backup / "manifest.json", encoded(manifest))
            if previous.exists(): shutil.rmtree(previous)
            published_mods.add(mod_dir)
        else:
            write_atomic(args.home / rel, data)
            manifest[rel]["installed"] = digest(data)
            manifest[rel]["applied"] = True
            write_atomic(backup / "manifest.json", encoded(manifest))
    print("Installed. Run mise check, then verify the dialogs in the app.")

if __name__ == "__main__":
    try: main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
