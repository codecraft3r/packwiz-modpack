#!/usr/bin/env python3
"""Check release parity, required mods, sidedness, and Packwiz integrity offline."""
import hashlib
import json
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads((ROOT / path).read_text())


def digest(path, algorithm):
    return hashlib.new(algorithm, path.read_bytes()).hexdigest()


def validate():
    source = read_json("docs/createa-colony/source.json")
    manifest = read_json("docs/createa-colony/upstream-manifest.json")
    overrides = read_json("docs/createa-colony/upstream-overrides.json")
    sides = read_json("docs/createa-colony/client-only.json")
    client_ids = {item["project_id"] for item in sides}
    pack = tomllib.loads((ROOT / "pack.toml").read_text())
    assert pack["versions"] == {
        "minecraft": source["minecraft"], "neoforge": source["neoforge"]
    }, "Loader versions differ from the upstream release"
    assert pack["version"] == source["pack_version"], "Pack version mismatch"
    index_path = ROOT / pack["index"]["file"]
    assert digest(index_path, pack["index"]["hash-format"]) == pack["index"]["hash"], "Stale pack hash"
    index = tomllib.loads(index_path.read_text())
    indexed = set()
    metadata_paths = set()
    for entry in index["files"]:
        name = entry["file"]
        path = ROOT / name
        assert path.resolve().is_relative_to(ROOT), f"Unsafe index path: {name}"
        assert name not in indexed, f"Duplicate index entry: {name}"
        indexed.add(name)
        assert path.is_file(), f"Missing indexed file: {name}"
        assert digest(path, entry.get("hash-format", index["hash-format"])) == entry["hash"], f"Stale hash: {name}"
        if entry.get("metafile"):
            metadata_paths.add(name)
        assert path.suffix not in {".jar", ".zip", ".mrpack", ".py"}, f"Build artifact in pack: {name}"
        assert path.parts[len(ROOT.parts)] not in {"docs", "scripts", ".github", "backups"}, f"Developer file in pack: {name}"
    expected = {(item["projectID"], item["fileID"]) for item in manifest["files"]}
    actual = set()
    filenames = set()
    mod_paths = {p.relative_to(ROOT).as_posix() for p in ROOT.glob("mods/*.pw.toml")}
    assert metadata_paths == mod_paths, "Unindexed mods or unexpected metadata"
    for name in sorted(mod_paths):
        mod = tomllib.loads((ROOT / name).read_text())
        cf = mod["update"]["curseforge"]
        pair = cf["project-id"], cf["file-id"]
        assert pair not in actual, f"Duplicate mod: {name}"
        actual.add(pair)
        assert mod["filename"] not in filenames, f"Duplicate jar name: {name}"
        filenames.add(mod["filename"])
        assert not mod.get("option", {}).get("optional", False), f"Optional mod: {name}"
        assert mod["side"] == ("client" if pair[0] in client_ids else "both"), f"Wrong install side: {name}"
        download = mod["download"]
        assert download.get("mode") == "metadata:curseforge", f"Unexpected download source: {name}"
        length = hashlib.new(download["hash-format"]).digest_size * 2
        assert len(download["hash"]) == length and all(c in "0123456789abcdef" for c in download["hash"]), f"Invalid download hash: {name}"
    assert actual == expected, f"Manifest mismatch: missing={expected-actual}, extra={actual-expected}"
    assert len(actual) == source["mods"] == 122, "Unexpected mod count"
    assert client_ids <= {pair[0] for pair in actual}, "Unknown client-only project"
    assert indexed == set(overrides) | mod_paths, "Unexpected files in the distributed pack"
    for name, expected_hash in overrides.items():
        assert name in indexed, f"Unindexed upstream override: {name}"
        assert digest(ROOT / name, "sha256") == expected_hash, f"Modified upstream override: {name}"
    assert len(overrides) == source["overrides"], "Override count mismatch"
    print(f"PASS: {len(actual)} required mods ({len(actual)-len(client_ids)} server, {len(client_ids)} client-only), "
          f"{len(overrides)} unchanged upstream overrides, {len(indexed)} verified index hashes")


if __name__ == "__main__":
    try:
        validate()
    except (AssertionError, KeyError, ValueError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
