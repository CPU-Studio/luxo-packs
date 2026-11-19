#!/usr/bin/env python3
"""Builds and signs the pack index that the Luxo app reads.

    python3 pack_index.py keygen [--key PATH]
        Makes an ECDSA P-256 signing key (default ~/.config/luxo3d/index-key.pem,
        kept private) and prints the public key line to put in the app
        (PackIndex.TRUSTED_KEYS).

    python3 pack_index.py build ZIPDIR --out OUTDIR [--key PATH] [--withdrawn id@version,...]
        Checks every pack <id>-<version>.zip in ZIPDIR and its source bundle
        <id>-<version>-src.zip (registry_check.py; a pack without one is
        skipped), copies both to OUTDIR/packs/, extracts a preview image if the
        pack has one, and writes OUTDIR/index.json, OUTDIR/index.json.sig (the
        signature the app checks) and OUTDIR/index.key (the public key, for
        people who add this index as a private source).  Serve OUTDIR over
        HTTPS; the app is given the URL of index.json.

    python3 pack_index.py publish REGISTRY [--key PATH] [--withdrawn id@version,...]
        The same for a registry repository served as it is (GitHub Pages): the
        zips stay in REGISTRY/submissions/, and index.json, its .sig, index.key
        and previews/ are written at REGISTRY's top.  Commit and push them.

index.json, format 1:
  { "format": 1, "generated": "...", "packs": [
      { "id", "version", "title", "authors", "license", "tier", "base",
        "targets": [{"system", "sha1": [...]}],
        "url": "packs/<id>-<version>.zip", "sha256", "size",
        "source_url": "packs/<id>-<version>-src.zip", "source_sha256", "source_size",
        "derived_from": "<id>@<version>" or null,
        "preview": "packs/<id>-<version>.png" or null, "withdrawn": false } ] }
URLs are relative to index.json.  Withdrawn packs stay listed (so the app can
tell people) but are not offered for download.
"""

import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registry_check import check_sources, check_zip  # noqa: E402

DEFAULT_KEY = os.path.expanduser("~/.config/luxo3d/index-key.pem")


def arg(args, name, default=None):
    if name in args:
        i = args.index(name)
        value = args[i + 1]
        del args[i:i + 2]
        return value
    return default


def public_key_b64(key):
    der = subprocess.run(["openssl", "pkey", "-in", key, "-pubout", "-outform", "DER"],
                         capture_output=True, check=True).stdout
    import base64
    return base64.b64encode(der).decode()


def keygen(args):
    key = arg(args, "--key", DEFAULT_KEY)
    if os.path.exists(key):
        sys.exit("%s exists already; not overwriting a signing key" % key)
    os.makedirs(os.path.dirname(key), exist_ok=True)
    old = os.umask(0o077)
    try:
        subprocess.run(["openssl", "genpkey", "-algorithm", "EC", "-pkeyopt", "ec_paramgen_curve:P-256",
                        "-out", key], check=True, capture_output=True)
    finally:
        os.umask(old)
    print("private key: %s (keep it private and backed up)" % key)
    print("public key for the app (PackIndex.TRUSTED_KEYS):")
    print(public_key_b64(key))


def make_index(zipdir, key, withdrawn, place):
    """Checks the packs in zipdir and writes the signed index.  place(path, kind)
    puts a file where it is served and returns its URL relative to index.json
    (kind: "zip", "src" or "preview").  Returns (index path, failures)."""
    zips = sorted(f for f in os.listdir(zipdir) if f.endswith(".zip") and not f.endswith("-src.zip"))
    entries, failed = [], 0
    for name in zips:
        src = os.path.join(zipdir, name)
        problems, pack = check_zip(src)
        srcbundle = src[:-len(".zip")] + "-src.zip"
        if not problems:
            if not os.path.exists(srcbundle):
                problems = ["no source bundle %s" % os.path.basename(srcbundle)]
            else:
                problems = check_sources(srcbundle)[0]
        if problems:
            failed += 1
            print("skipped %s: %s" % (name, "; ".join(problems)))
            continue
        base = "%s-%s" % (pack["id"], pack["version"])
        data = open(src, "rb").read()
        sdata = open(srcbundle, "rb").read()
        preview = None
        with zipfile.ZipFile(src) as z:
            pngs = sorted(n for n in z.namelist() if n.startswith("preview") and n.endswith(".png"))
            if pngs:
                tmp = os.path.join(zipdir, ".%s.png" % base)
                with open(tmp, "wb") as f:
                    f.write(z.read(pngs[0]))
                preview = place(tmp, "preview", base + ".png")
                os.remove(tmp)
            has_models = any(n.endswith(".glb") for n in z.namelist())
        entries.append({
            "id": pack["id"], "version": pack["version"], "title": pack["title"],
            "authors": pack.get("authors", []), "license": pack["license"],
            "tier": pack.get("tier") or ("sculpted" if has_models else "voxel"),
            "base": pack.get("base") or None,
            "derived_from": pack.get("derived_from") or None,
            "targets": pack["targets"],
            "url": place(src, "zip", base + ".zip"),
            "sha256": hashlib.sha256(data).hexdigest(), "size": len(data),
            "source_url": place(srcbundle, "src", base + "-src.zip"),
            "source_sha256": hashlib.sha256(sdata).hexdigest(), "source_size": len(sdata),
            "preview": preview, "withdrawn": "%s@%s" % (pack["id"], pack["version"]) in withdrawn,
        })
    index = {"format": 1,
             "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "packs": entries}
    return index, failed


def write_signed(index, outdir, key):
    path = os.path.join(outdir, "index.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1)
        f.write("\n")
    subprocess.run(["openssl", "dgst", "-sha256", "-sign", key, "-out", path + ".sig", path], check=True)
    pub = public_key_b64(key)
    with open(os.path.join(outdir, "index.key"), "w") as f:
        f.write(pub + "\n")
    return path, pub


def build(args):
    key = arg(args, "--key", DEFAULT_KEY)
    out = arg(args, "--out")
    withdrawn = set(filter(None, (arg(args, "--withdrawn", "") or "").split(",")))
    if len(args) != 1 or not out:
        sys.exit("usage: pack_index.py build ZIPDIR --out OUTDIR [--key PATH] [--withdrawn id@version,...]")
    if not os.path.exists(key):
        sys.exit("no signing key at %s (run: pack_index.py keygen)" % key)
    os.makedirs(os.path.join(out, "packs"), exist_ok=True)

    def place(path, kind, name):
        shutil.copyfile(path, os.path.join(out, "packs", name))
        return "packs/" + name

    index, failed = make_index(args[0], key, withdrawn, place)
    path, pub = write_signed(index, out, key)
    print("wrote %s (%d packs, %d skipped) and its signature; public key %s" % (
        path, len(index["packs"]), failed, pub[:24] + "..."))
    return 1 if failed else 0


def publish(args):
    key = arg(args, "--key", DEFAULT_KEY)
    withdrawn = set(filter(None, (arg(args, "--withdrawn", "") or "").split(",")))
    if len(args) != 1:
        sys.exit("usage: pack_index.py publish REGISTRY [--key PATH] [--withdrawn id@version,...]")
    if not os.path.exists(key):
        sys.exit("no signing key at %s (run: pack_index.py keygen)" % key)
    reg = args[0]
    subs = os.path.join(reg, "submissions")
    os.makedirs(os.path.join(reg, "previews"), exist_ok=True)

    def place(path, kind, name):
        if kind == "preview":
            shutil.copyfile(path, os.path.join(reg, "previews", name))
            return "previews/" + name
        return "submissions/" + os.path.basename(path)

    index, failed = make_index(subs, key, withdrawn, place)
    path, pub = write_signed(index, reg, key)
    print("wrote %s (%d packs, %d skipped), index.json.sig and index.key; public key %s" % (
        path, len(index["packs"]), failed, pub[:24] + "..."))
    print("now commit index.json, index.json.sig, index.key and previews/, and push")
    return 1 if failed else 0


def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("keygen", "build", "publish"):
        sys.exit(__doc__)
    cmd = args.pop(0)
    sys.exit({"keygen": keygen, "build": build, "publish": publish}[cmd](args))


if __name__ == "__main__":
    main()
