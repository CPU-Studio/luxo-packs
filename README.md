# Luxo 3D packs

The public list of 3D packs for the Luxo emulator's 3D view. Each pack is a zip of rules
(tile hashes, roles, scenes, effects) and original 3D models. The Luxo app reads the signed
`index.json` published from here, offers the packs that fit the game being played, and
checks every download against the index.

**New to this? [GUIDE.md](GUIDE.md) walks you through making a pack with an AI agent
(Claude Code, Codex, OpenCode, …), step by step, no coding needed.**

Every pack here can be edited: a pack with models comes with its **sources** (its Blender
files and the scripts that rebuild it), and a rules-only pack is its own source. Anyone can
improve a pack with their own agent (`pack_fork.py`) and offer the result back.

## Submitting a pack

Open a pull request that adds to `submissions/` the pack and, if it has models, its sources:

| File | What | Made with |
|---|---|---|
| `<id>-<version>.zip` | the pack, as the app installs it | `luxo3d package PACKDIR --out …` |
| `<id>-<version>-src.zip` | its sources: the pack plus `sources/` with every model's `.blend` file and the scripts that rebuild the models and rules. Not needed for a rules-only pack (no models), whose `pack.json` is its source. | `pack_sources.py PACKDIR --out …` |

CI checks what you submit (`tools/registry_check.py`). The pack's `pack.json` needs:
- `id` (lowercase letters, digits and `-`), `version`, `title`, `license`, `authors`;
- `targets` listing the ROM IDs (SHA-1) it fits.

The pack holds only `.json`, `.glb`, `.png`, `.ktx2` and `.md` files (50 MB at most). The
sources may also hold `.blend`, `.py` and `.txt` (90 MB at most); a `.blend` must not
contain text blocks (embedded scripts), scripted drivers or links to other files. To update
a pack, submit it again (with its sources, if it has models) with a higher `version`.

An edit of someone else's pack keeps `"derived_from": "<id>@<version>"` (`pack_fork.py`
writes it), credits the original authors, and follows their licence.

## What is accepted

The maintainer reviews every pack for copyright before merging. Accepted:
- **original designs**: characters made up to fill a sprite's role (a hero, a racer, an
  enemy of that size and colours), not copies of the game's characters;
- **generic objects**: trees, houses, karts, coins, crates, pipes, shells;
- **rules only** (voxel packs): their art is rebuilt on the player's own device from their
  own ROM, so the pack holds no game art;
- previews that show the pack's own 3D models.

Not accepted:
- ROMs, BIOS files, tiles or other graphics extracted from a game;
- models traced from a game's sprites (`sprite_to_glb.py`), or recreations of its
  characters, logos or levels;
- screenshots of the original game.

**Licence:** one that allows edits, such as CC-BY-4.0, CC-BY-SA-4.0 or CC0-1.0 (not "ND").
Packs here can be forked; that is the point of the sources.

**Packs with models must come with their sources**, so the maintainer can see how each model
was made, and anyone can edit it. To share a model pack without its sources, use a
private source or share the zip directly.

## Asking for a pack to be removed

Open an issue titled `Removal: <pack id>` that says who you are and why. A rights holder's
request is honoured: the maintainer marks the pack withdrawn, publishes a new index (the
app stops offering it) and deletes its files.

## Publishing (maintainer)

After merging pull requests, on the maintainer's machine, with the signing key:

```
python3 tools/pack_index.py publish .                    # [--withdrawn id@version,...]
git add index.json index.json.sig index.key previews && git commit -m "Publish the index" && git push
```

`publish` checks every pack and its sources again and writes the signed `index.json` at the
top of the repository. GitHub Pages (`.github/workflows/pages.yml`) serves the repository as
it is, so the zips stay in `submissions/`.

The signing key (`~/.config/luxo3d/index-key.pem`, made by `pack_index.py keygen`) never
goes into this repository or into CI. The app trusts only the public keys built into it, so
a copied or altered index is refused. `index.key` is the public half, for people who add
this list as a source by hand.
