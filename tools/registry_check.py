#!/usr/bin/env python3
"""Checks pack zips before they go into a pack index (run by the registry's CI).

    python3 registry_check.py pack.zip [pack.zip ...] [--luxo3d PATH] [--blender PATH]

A file named <id>-<version>-src.zip is a source bundle (see pack_sources.py) and
gets the source checks below; any other zip is a pack (what the app installs).

Checks, without trusting anything inside the zip:
- file names: no absolute paths, no "..", only .json .glb .png .ktx2 .md files,
  pack.json at the top level, at most 256 files and 50 MB unpacked;
- no ROM data: no file starts with an iNES header ("NES\\x1A");
- pack.json: schema 1, an id (lowercase letters, digits, -), a version, a title,
  a licence, and targets with 40-digit SHA-1 ROM IDs.
With --luxo3d it also unpacks each zip and runs "luxo3d validate" (the app's
own pack and model readers).

A pack with models (.glb files) needs its source bundle beside it.  A
rules-only pack (no models: voxel packs, whose art is rebuilt from the
player's own ROM) needs none: its pack.json is its source.

Source bundles (what people edit with their agents; see pack_fork.py):
- the same path checks, with .blend .py and .txt allowed as well, at most
  2048 files and 90 MB (GitHub's limit is 100 MB a file);
- pack.json at the top level, as in the pack, with a licence that allows
  edits (no "ND" licences);
- for a pack with models, at least one .blend and one .py (the scripts that
  rebuild the models);
- the pack beside it (same name without -src) has the same id and version;
- with --blender, every .blend is opened with scripts off and refused if it
  holds text blocks (embedded scripts), scripted drivers or linked library
  files: Blender can run those when someone opens the file.

Exit status 1 if any zip fails.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

ALLOWED = {".json", ".glb", ".png", ".ktx2", ".md"}
MAX_FILES = 256
MAX_BYTES = 50 * 1024 * 1024
SOURCE_ALLOWED = ALLOWED | {".blend", ".py", ".txt"}
SOURCE_MAX_FILES = 2048
SOURCE_MAX_BYTES = 90 * 1024 * 1024
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")


def has_models(path):
    """Whether a pack zip holds models (.glb); False when it cannot be read."""
    try:
        with zipfile.ZipFile(path) as z:
            return any(n.lower().endswith(".glb") for n in z.namelist())
    except (OSError, zipfile.BadZipFile):
        return False


def is_source_bundle(path):
    return os.path.basename(path).endswith("-src.zip")


def check_entries(z, allowed, max_files, max_bytes):
    """Path, type, size and ROM-data checks on a zip's entries."""
    problems = []
    infos = z.infolist()
    if len(infos) > max_files:
        problems.append("%d files; the limit is %d" % (len(infos), max_files))
    total = 0
    for i in infos:
        name = i.filename
        if name.endswith("/"):
            continue
        parts = name.split("/")
        if name.startswith("/") or "\\" in name or ".." in parts or ":" in name:
            problems.append("unsafe path: %s" % name)
        elif any(p.startswith(".") for p in parts):
            problems.append("hidden file: %s" % name)
        ext = os.path.splitext(name)[1].lower()
        if ext not in allowed:
            problems.append("file type not allowed: %s" % name)
        total += i.file_size
        with z.open(i) as f:
            if f.read(4) == b"NES\x1a":
                problems.append("contains ROM data (iNES header): %s" % name)
    if total > max_bytes:
        problems.append("%d bytes unpacked; the limit is %d" % (total, max_bytes))
    return problems


def check_zip(path, luxo3d=None):
    try:
        z = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as e:
        return ["not a zip file: %s" % e], None
    problems = check_entries(z, ALLOWED, MAX_FILES, MAX_BYTES)

    pack = None
    if "pack.json" not in z.namelist():
        problems.append("no pack.json at the top level")
    else:
        try:
            pack = json.loads(z.read("pack.json"))
        except ValueError as e:
            problems.append("pack.json is not JSON: %s" % e)
    if pack is not None:
        if pack.get("schema") != 1:
            problems.append("schema must be 1")
        if not ID_RE.match(str(pack.get("id", ""))):
            problems.append("id must be lowercase letters, digits and -, 2-64 long")
        for field in ("version", "title", "license"):
            if not str(pack.get(field, "")).strip():
                problems.append("missing %s" % field)
        targets = pack.get("targets") or []
        hashes = [h for t in targets for h in t.get("sha1", [])]
        if not hashes:
            problems.append("no targets")
        for h in hashes:
            if not SHA1_RE.match(str(h).lower()):
                problems.append("bad ROM ID in targets: %s" % h)

    if luxo3d and not problems:
        with tempfile.TemporaryDirectory() as tmp:
            z.extractall(tmp)
            p = subprocess.run([luxo3d, "validate", tmp], capture_output=True, text=True)
            if p.returncode != 0:
                problems.append("luxo3d validate: " + (p.stdout + p.stderr).strip())
    return problems, pack


# Run inside Blender (scripts off): reports what in a .blend could run code.
BLEND_PROBE = r"""
import bpy, json, sys
path = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
drivers = 0
for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.shape_keys,
             bpy.data.armatures, bpy.data.node_groups, bpy.data.scenes, bpy.data.worlds):
    for idb in coll:
        ad = getattr(idb, "animation_data", None)
        for d in (ad.drivers if ad else []):
            if d.driver.type == "SCRIPTED":
                drivers += 1
print("BLENDPROBE " + json.dumps({"texts": [t.name for t in bpy.data.texts],
                                  "drivers": drivers,
                                  "libraries": [l.filepath for l in bpy.data.libraries]}))
"""


def check_blend(path, blender):
    """Problems in one .blend file, found by opening it in Blender with scripts off."""
    p = subprocess.run([blender, "--background", "--factory-startup", "--disable-autoexec",
                        "--python-expr", BLEND_PROBE, "--", path],
                       capture_output=True, text=True, timeout=300)
    line = next((l for l in p.stdout.splitlines() if l.startswith("BLENDPROBE ")), None)
    if line is None:
        return ["Blender could not open it: " + (p.stderr or p.stdout).strip()[-300:]]
    info = json.loads(line[len("BLENDPROBE "):])
    problems = []
    if info["texts"]:
        problems.append("holds text blocks (embedded scripts): %s; keep scripts in .py files"
                        % ", ".join(info["texts"]))
    if info["drivers"]:
        problems.append("has %d scripted driver(s)" % info["drivers"])
    if info["libraries"]:
        problems.append("links library files: %s" % ", ".join(info["libraries"]))
    return problems


def check_sources(path, blender=None):
    """Checks a source bundle (<id>-<version>-src.zip).  Returns (problems, pack)."""
    try:
        z = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as e:
        return ["not a zip file: %s" % e], None
    problems = check_entries(z, SOURCE_ALLOWED, SOURCE_MAX_FILES, SOURCE_MAX_BYTES)
    names = [n for n in z.namelist() if not n.endswith("/")]
    blends = [n for n in names if n.lower().endswith(".blend")]
    if any(n.lower().endswith(".glb") for n in names):
        if not blends:
            problems.append("no .blend file (the models to edit)")
        if not any(n.lower().endswith(".py") for n in names):
            problems.append("no .py file (the scripts that rebuild the models)")
    pack = None
    if "pack.json" not in names:
        problems.append("no pack.json at the top level")
    else:
        try:
            pack = json.loads(z.read("pack.json"))
        except ValueError as e:
            problems.append("pack.json is not JSON: %s" % e)
    if pack is not None:
        lic = str(pack.get("license", ""))
        if not lic.strip():
            problems.append("missing license")
        elif re.search(r"(^|[-_ ])ND([-_ ]|$)", lic.upper()):
            problems.append("licence %s does not allow edits" % lic)
        runtime = path[:-len("-src.zip")] + ".zip"
        if not os.path.exists(runtime):
            problems.append("no pack beside it (%s)" % os.path.basename(runtime))
        else:
            _, rpack = check_zip(runtime)
            if rpack and (rpack.get("id"), rpack.get("version")) != (pack.get("id"), pack.get("version")):
                problems.append("id/version differ from %s" % os.path.basename(runtime))
    if blender and not problems:
        with tempfile.TemporaryDirectory() as tmp:
            for n in blends:
                z.extract(n, tmp)
                for p in check_blend(os.path.join(tmp, n), blender):
                    problems.append("%s: %s" % (n, p))
    return problems, pack


def main():
    args = sys.argv[1:]
    luxo3d = blender = None
    if "--luxo3d" in args:
        i = args.index("--luxo3d")
        luxo3d = args[i + 1]
        del args[i:i + 2]
    if "--blender" in args:
        i = args.index("--blender")
        blender = args[i + 1]
        del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    failed = 0
    for path in args:
        if is_source_bundle(path):
            problems, pack = check_sources(path, blender)
        else:
            problems, pack = check_zip(path, luxo3d)
            src = path[:-len(".zip")] + "-src.zip"
            if not problems and not os.path.exists(src) and has_models(path):
                problems.append("it has models but no source bundle beside it (%s; see pack_sources.py)"
                                % os.path.basename(src))
        if problems:
            failed += 1
            print("FAIL %s" % path)
            for p in problems:
                print("  - " + p)
        else:
            print("ok   %s: %s %s" % (path, pack["id"], pack["version"]))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
