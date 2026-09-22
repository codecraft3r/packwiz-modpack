#!/usr/bin/env python3
"""Check release parity, required mods, sidedness, and Packwiz integrity offline."""
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path, algorithm):
    return hashlib.new(algorithm, path.read_bytes()).hexdigest()


def validate():
    source = read_json("docs/createa-colony/source.json")
    manifest = read_json("docs/createa-colony/upstream-manifest.json")
    overrides = read_json("docs/createa-colony/upstream-overrides.json")
    sides = read_json("docs/createa-colony/client-only.json")
    client_ids = {item["project_id"] for item in sides}
    pack = tomllib.loads((ROOT / "pack.toml").read_text(encoding="utf-8"))
    assert pack["versions"] == {
        "minecraft": source["minecraft"], "neoforge": source["neoforge"]
    }, "Loader versions differ from the upstream release"
    assert pack["version"] == source["pack_version"], "Pack version mismatch"
    index_path = ROOT / pack["index"]["file"]
    assert digest(index_path, pack["index"]["hash-format"]) == pack["index"]["hash"], "Stale pack hash"
    index = tomllib.loads(index_path.read_text(encoding="utf-8"))
    tracked = set(subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT
    ).decode().split("\0"))
    indexed = set()
    metadata_paths = set()
    for entry in index["files"]:
        name = entry["file"]
        path = ROOT / name
        assert path.resolve().is_relative_to(ROOT), f"Unsafe index path: {name}"
        assert name not in indexed, f"Duplicate index entry: {name}"
        indexed.add(name)
        assert path.is_file(), f"Missing indexed file: {name}"
        assert name in tracked, f"Indexed file is not committed or staged: {name}"
        assert digest(path, entry.get("hash-format", index["hash-format"])) == entry["hash"], f"Stale hash: {name}"
        if entry.get("metafile"):
            metadata_paths.add(name)
        assert path.suffix not in {".jar", ".zip", ".mrpack", ".py"}, f"Build artifact in pack: {name}"
        assert path.parts[len(ROOT.parts)] not in {"docs", "scripts", ".github", "backups"}, f"Developer file in pack: {name}"
    # Mods that were removed or migrated away from CurseForge due to API distribution blocks
    MIGRATED_OR_REMOVED_CF = {
        1558694,  # Aeronautics:No Horizon (removed)
        1527587,  # Farmer's Sandwiches (removed)
        1332665,  # CreateColonies (moved to GitHub direct release)
        525480,   # Better Villages (moved to Modrinth)
        1520961,  # Copycats+ aeronautics weight (moved to Modrinth)
        676721,   # Create Aeronautics (moved to Modrinth)
        1556708,  # Create: Linear Bearing (moved to Modrinth)
        522351,   # Library Ferret (moved to Modrinth)
        1497043,  # Middgard (moved to Modrinth)
        521480,   # Skin Layers 3D (moved to Modrinth)
        962544,   # Oh The Trees You'll Grow (updated on Modrinth for Middgard dependency)
        533097,   # C2ME (moved to Modrinth)
    }
    expected = {
        (item["projectID"], item["fileID"])
        for item in manifest["files"]
        if item["projectID"] not in MIGRATED_OR_REMOVED_CF
    }
    actual_cf = set()
    filenames = set()
    all_pw_paths = {p.relative_to(ROOT).as_posix() for p in ROOT.glob("**/*.pw.toml")}
    assert metadata_paths == all_pw_paths, f"Unindexed mods or unexpected metadata: {metadata_paths ^ all_pw_paths}"
    for name in sorted(all_pw_paths):
        mod = tomllib.loads((ROOT / name).read_text(encoding="utf-8"))
        assert mod["filename"] not in filenames, f"Duplicate jar/pack name: {name}"
        filenames.add(mod["filename"])
        assert not mod.get("option", {}).get("optional", False), f"Optional mod: {name}"
        download = mod["download"]
        length = hashlib.new(download["hash-format"]).digest_size * 2
        assert len(download["hash"]) == length and all(c in "0123456789abcdef" for c in download["hash"]), f"Invalid download hash: {name}"
        if "curseforge" in mod.get("update", {}):
            cf = mod["update"]["curseforge"]
            pair = cf["project-id"], cf["file-id"]
            actual_cf.add(pair)
            if pair[0] in client_ids:
                assert mod["side"] == "client", f"Wrong install side: {name}"
    missing_upstream = expected - actual_cf
    assert not missing_upstream, f"Missing upstream mods from manifest: {missing_upstream}"
    for name, expected_hash in overrides.items():
        assert name in indexed, f"Unindexed upstream override: {name}"
        assert digest(ROOT / name, "sha256") == expected_hash, f"Modified upstream override: {name}"
    assert len(overrides) == source["overrides"], "Override count mismatch"
    print(f"PASS: {len(all_pw_paths)} metadata files ({len(actual_cf)} CurseForge, {len(all_pw_paths)-len(actual_cf)} Modrinth/other), "
          f"{len(overrides)} unchanged upstream overrides, {len(indexed)} verified index hashes")


if __name__ == "__main__":
    try:
        validate()
    except (AssertionError, KeyError, ValueError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
