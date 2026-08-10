#!/usr/bin/env python3
"""Create a compact, reproducible discovery bundle for the VvH quest campaign.

The workflow clones the authoritative pack, optionally materializes its server files,
and invokes this script with the clone and runtime paths. The output intentionally
contains metadata and text resources rather than redistributing third-party JARs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
import tomllib
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

TEXT_SUFFIXES = {
    ".snbt", ".toml", ".json", ".json5", ".js", ".py", ".md", ".txt",
    ".properties", ".cfg", ".conf", ".yml", ".yaml", ".mcmeta", ".lang",
}
COPY_ROOTS = (
    "config/ftbquests",
    "config/ftbchunks-client.snbt",
    "config/ftbchunks-world.snbt",
    "config/ftbteams",
    "config/kubejs-client.toml",
    "config/kubejs-common.toml",
    "config/kubejs-startup.toml",
    "kubejs",
    "local",
    "global_packs/required_resources",
    "scripts",
    "docs",
    ".github/workflows",
)
ROOT_FILES = (
    "pack.toml", "index.toml", ".packwizignore", "README.md", "CHANGELOG.md",
    "agents.md", "AGENTS.md",
)
SELECTED_JAR_KEYWORDS = (
    "ftb-quests", "ftbquests", "ftb-teams", "ftbteams", "ftb-chunks", "ftbchunks",
    "kubejs", "rhino", "architectury", "create", "numismatics", "vampir",
    "hunter", "irons_spellbooks", "cobblemon", "waystones", "explorerscompass",
    "patchouli", "resourcefullib", "resourcefulconfig",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_read(path: Path, limit: int = 8_000_000) -> str | None:
    try:
        if path.stat().st_size > limit:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        return None


def copy_path(src_root: Path, rel: str, dst_root: Path) -> None:
    src = src_root / rel
    if not src.exists():
        return
    dst = dst_root / rel
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.jar", "*.zip", ".git"))
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def iter_pack_metadata(pack_root: Path) -> Iterable[Path]:
    yield from sorted(pack_root.rglob("*.pw.toml"))


def parse_mod_metadata(pack_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in iter_pack_metadata(pack_root):
        rel = path.relative_to(pack_root).as_posix()
        try:
            doc = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            rows.append({"path": rel, "parse_error": str(exc)})
            continue
        download = doc.get("download", {})
        update = doc.get("update", {})
        row = {
            "path": rel,
            "name": doc.get("name"),
            "filename": doc.get("filename"),
            "side": doc.get("side", "both"),
            "hash_format": download.get("hash-format"),
            "hash": download.get("hash"),
            "url": download.get("url"),
            "mode": download.get("mode"),
            "update_providers": sorted(update.keys()),
        }
        for provider, values in update.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    row[f"{provider}_{key}"] = value
        rows.append(row)
    return rows


def extract_mod_descriptors(zf: zipfile.ZipFile) -> dict[str, str]:
    wanted = [
        "META-INF/neoforge.mods.toml",
        "META-INF/mods.toml",
        "fabric.mod.json",
        "quilt.mod.json",
        "META-INF/MANIFEST.MF",
    ]
    out: dict[str, str] = {}
    names = set(zf.namelist())
    for name in wanted:
        if name in names:
            try:
                out[name] = zf.read(name).decode("utf-8", errors="replace")
            except Exception as exc:  # noqa: BLE001
                out[name] = f"<read error: {exc}>"
    return out


def catalog_jar(path: Path, descriptor_root: Path, index_root: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "filename": path.name,
        "size": path.stat().st_size,
        "sha256": sha256(path),
        "selected_for_index": any(k in path.name.lower() for k in SELECTED_JAR_KEYWORDS),
    }
    try:
        with zipfile.ZipFile(path) as zf:
            names = sorted(zf.namelist())
            info["entry_count"] = len(names)
            descriptors = extract_mod_descriptors(zf)
            info["descriptor_files"] = sorted(descriptors)
            if descriptors:
                out_dir = descriptor_root / path.stem
                out_dir.mkdir(parents=True, exist_ok=True)
                for descriptor_name, text in descriptors.items():
                    flat = descriptor_name.replace("/", "__")
                    (out_dir / flat).write_text(text, encoding="utf-8")

            assets: dict[str, set[str]] = defaultdict(set)
            data_ids: dict[str, set[str]] = defaultdict(set)
            for name in names:
                match = re.match(r"assets/([^/]+)/models/item/(.+)\.json$", name)
                if match:
                    assets["items"].add(f"{match.group(1)}:{match.group(2)}")
                match = re.match(r"assets/([^/]+)/models/block/(.+)\.json$", name)
                if match:
                    assets["blocks"].add(f"{match.group(1)}:{match.group(2)}")
                match = re.match(r"assets/([^/]+)/textures/(.+)\.png$", name)
                if match:
                    assets["textures"].add(f"{match.group(1)}:textures/{match.group(2)}.png")
                match = re.match(r"data/([^/]+)/(?:advancement|advancements)/(.+)\.json$", name)
                if match:
                    data_ids["advancements"].add(f"{match.group(1)}:{match.group(2)}")
                match = re.match(r"data/([^/]+)/(?:recipe|recipes)/(.+)\.json$", name)
                if match:
                    data_ids["recipes"].add(f"{match.group(1)}:{match.group(2)}")
            info["catalog_counts"] = {k: len(v) for k, v in {**assets, **data_ids}.items()}
            if info["selected_for_index"]:
                index_root.mkdir(parents=True, exist_ok=True)
                (index_root / f"{path.name}.entries.txt").write_text("\n".join(names) + "\n", encoding="utf-8")
                for category, values in {**assets, **data_ids}.items():
                    if values:
                        (index_root / f"{path.name}.{category}.txt").write_text(
                            "\n".join(sorted(values)) + "\n", encoding="utf-8"
                        )
    except zipfile.BadZipFile as exc:
        info["error"] = f"bad zip: {exc}"
    except Exception as exc:  # noqa: BLE001
        info["error"] = repr(exc)
    return info


def inventory_text_files(pack_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(pack_root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(pack_root).as_posix()
        text = safe_read(path)
        rows.append({
            "path": rel,
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "lines": None if text is None else text.count("\n") + 1,
        })
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    keys: list[str] = sorted({key for row in rows for key in row})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def make_tree(pack_root: Path) -> str:
    lines: list[str] = []
    for path in sorted(pack_root.rglob("*")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(pack_root).as_posix()
        if path.is_dir():
            lines.append(rel + "/")
        else:
            lines.append(f"{rel}\t{path.stat().st_size}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    args = parser.parse_args()

    pack_root = args.pack.resolve()
    runtime_root = args.runtime.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    source_copy = out / "source"
    for rel in ROOT_FILES:
        copy_path(pack_root, rel, source_copy)
    for rel in COPY_ROOTS:
        copy_path(pack_root, rel, source_copy)
    # Pack metadata is small and is required to resolve exact versions/licences.
    for meta in iter_pack_metadata(pack_root):
        dest = source_copy / meta.relative_to(pack_root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(meta, dest)

    mods = parse_mod_metadata(pack_root)
    (out / "packwiz-mods.json").write_text(json.dumps(mods, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(mods, out / "packwiz-mods.csv")
    text_files = inventory_text_files(pack_root)
    (out / "text-inventory.json").write_text(json.dumps(text_files, indent=2), encoding="utf-8")
    (out / "repo-tree.txt").write_text(make_tree(pack_root), encoding="utf-8")

    jars = sorted(runtime_root.rglob("*.jar")) if runtime_root.exists() else []
    jar_rows: list[dict[str, Any]] = []
    descriptor_root = out / "jar-descriptors"
    index_root = out / "jar-index"
    for jar in jars:
        jar_rows.append(catalog_jar(jar, descriptor_root, index_root))
    (out / "runtime-jars.json").write_text(json.dumps(jar_rows, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(jar_rows, out / "runtime-jars.csv")

    pack_toml: dict[str, Any] = {}
    try:
        pack_toml = tomllib.loads((pack_root / "pack.toml").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        pack_toml = {"parse_error": repr(exc)}

    namespaces = Counter()
    for row in jar_rows:
        for descriptor_name in row.get("descriptor_files", []):
            namespaces[descriptor_name] += 1

    summary = {
        "source_repository": "codecraft3r/packwiz-modpack",
        "source_sha": args.source_sha,
        "pack": pack_toml,
        "packwiz_metadata_files": len(mods),
        "text_files": len(text_files),
        "runtime_available": runtime_root.exists(),
        "runtime_jar_count": len(jar_rows),
        "runtime_total_jar_bytes": sum(int(row.get("size", 0)) for row in jar_rows),
        "descriptor_type_counts": dict(namespaces),
        "quest_chapters": sorted(
            p.relative_to(pack_root).as_posix()
            for p in pack_root.glob("config/ftbquests/quests/chapters/*.snbt")
        ),
        "quest_language_files": sorted(
            p.relative_to(pack_root).as_posix()
            for p in pack_root.glob("config/ftbquests/quests/lang/*")
        ),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    archive = out.parent / "vvh-discovery-source.tar.gz"
    with tarfile.open(archive, "w:gz") as tf:
        tf.add(out, arcname="vvh-discovery")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
