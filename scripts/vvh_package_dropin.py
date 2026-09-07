#!/usr/bin/env python3
"""Package the intentional VvH repository delta as a reviewable drop-in ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ALLOWED_EXACT = {
    "CHANGELOG.md",
    "pack.toml",
    "index.toml",
    "config/ftbquests/quests/chapter_groups.snbt",
    "config/ftbquests/quests/lang/en_us.snbt",
    "global_packs/required_resources/poiesis_living_atlas_art.pw.toml",
}
ALLOWED_PREFIXES = (
    "config/ftbquests/quests/chapters/ch",
    "config/ftbquests/quests/reward_tables/",
    "docs/vvh/",
    "scripts/vvh_",
    "scripts/test_vvh_",
    ".github/workflows/",
    ".githooks/",
)


def run(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_allowed(rel: str) -> bool:
    return rel in ALLOWED_EXACT or any(rel.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def current_campaign_shape(root: Path) -> tuple[list[str], list[str]]:
    """Return the current generated chapter/table paths from live source data.

    The package helper used to hard-code the retired ten-chapter campaign.  The
    five-chapter generator is now authoritative, so packaging must derive its
    expected shape from the manifest and the files it actually emits.
    """
    manifest_path = root / "docs/vvh/campaign_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read current campaign manifest {manifest_path}: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("architecture") != "five-chapter-vvh-current":
        raise SystemExit(
            "Refusing to package a non-current campaign architecture: "
            f"{manifest.get('architecture')!r}" if isinstance(manifest, dict) else "<invalid manifest>"
        )
    chapters = [
        f"config/ftbquests/quests/chapters/{chapter['filename']}.snbt"
        for chapter in manifest.get("chapters", [])
        if isinstance(chapter, dict) and isinstance(chapter.get("filename"), str)
    ]
    tables = sorted(
        path.relative_to(root).as_posix()
        for path in (root / "config/ftbquests/quests/reward_tables").glob("*.snbt")
        if path.is_file()
    )
    if len(chapters) != 5 or not tables:
        raise SystemExit(
            "Current campaign shape is incomplete: "
            f"{len(chapters)} chapters and {len(tables)} reward tables"
        )
    missing = [relative for relative in [*chapters, *tables] if not (root / relative).is_file()]
    if missing:
        raise SystemExit("Current campaign files are missing:\n" + "\n".join(missing))
    return chapters, tables


def changed_paths(root: Path, base: str) -> list[str]:
    tracked = run(root, "diff", "--name-only", "--diff-filter=ACMRTUXB", base, "--").stdout.splitlines()
    untracked = run(root, "ls-files", "--others", "--exclude-standard", "-z").stdout.split("\0")
    paths = sorted({p for p in tracked + untracked if p})
    return paths


def deleted_paths(root: Path, base: str) -> list[str]:
    return sorted(
        p for p in run(root, "diff", "--name-only", "--diff-filter=D", base, "--").stdout.splitlines() if p
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--base", required=True)
    ap.add_argument("--zip", dest="zip_path", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--changed-list", type=Path, required=True)
    ap.add_argument("--patch", type=Path, required=True)
    args = ap.parse_args()

    root = args.root.resolve()
    paths = changed_paths(root, args.base)
    deleted = deleted_paths(root, args.base)
    unexpected_deletions = [p for p in deleted if not p.startswith("docs/vvh/evidence/")]
    if unexpected_deletions:
        raise SystemExit(f"Refusing to package deletions outside retired evidence: {unexpected_deletions}")
    if not paths:
        raise SystemExit("No changed files found")

    disallowed = [p for p in paths if not is_allowed(p)]
    if disallowed:
        raise SystemExit("Unexpected changed files outside VvH allowlist:\n" + "\n".join(disallowed))

    missing = [p for p in paths if not (root / p).is_file()]
    if missing:
        raise SystemExit("Changed paths are not regular files:\n" + "\n".join(missing))

    required = {
        "pack.toml",
        "index.toml",
        "config/ftbquests/quests/chapter_groups.snbt",
        "config/ftbquests/quests/lang/en_us.snbt",
        "docs/vvh/VALIDATION.md",
        "docs/vvh/VERIFICATION.md",
        "docs/vvh/UNRESOLVED.md",
        "docs/vvh/campaign_manifest.json",
        "scripts/vvh_campaign_v3.py",
        "scripts/vvh_campaign_v3_validate.py",
        "scripts/vvh_campaign_overrides.py",
        "scripts/vvh_sync_catalog.py",
        "scripts/vvh_render_layouts.py",
        "scripts/test_vvh_campaign_source.py",
    }
    missing_required = sorted(path for path in required if not (root / path).is_file())
    if missing_required:
        raise SystemExit("Required VvH deliverables are missing from the repository:\n" + "\n".join(missing_required))

    current_chapters, current_tables = current_campaign_shape(root)
    chapter_paths = [p for p in paths if p in current_chapters]
    table_paths = [p for p in paths if p in current_tables]
    changed_chapter_paths = set(chapter_paths)
    changed_table_paths = set(table_paths)
    unexpected_live_chapters = [
        p for p in paths
        if p.startswith("config/ftbquests/quests/chapters/") and p not in current_chapters
    ]
    if unexpected_live_chapters:
        raise SystemExit(
            "Unexpected non-current chapter files in drop-in delta:\n"
            + "\n".join(unexpected_live_chapters)
        )

    entries = []
    for rel in paths:
        path = root / rel
        entries.append({
            "path": rel,
            "size": path.stat().st_size,
            "sha256": sha256(path),
        })

    manifest = {
        "format": 1,
        "base_repository": "codecraft3r/packwiz-modpack",
        "base_sha": args.base,
        "file_count": len(entries),
        "campaign_architecture": "five-chapter-vvh-current",
        "chapters": len(current_chapters),
        "reward_tables": len(current_tables),
        "changed_chapters": sorted(changed_chapter_paths),
        "changed_reward_tables": sorted(changed_table_paths),
        "files": entries,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.changed_list.write_text("\n".join(paths) + "\n", encoding="utf-8")

    # The textual patch is supplemental; untracked files are represented in the ZIP + manifest.
    patch = run(root, "diff", "--binary", args.base, "--").stdout
    args.patch.write_text(patch, encoding="utf-8")

    args.zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in paths:
            zf.write(root / rel, PurePosixPath(rel).as_posix())
        zf.writestr("VVH_DROPIN_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        zf.writestr(
            "INSTALL.md",
            "# VvH Season One drop-in\n\n"
            f"Base revision: `{args.base}`.\n\n"
            "Extract into the root of `codecraft3r/packwiz-modpack`, review the diff, "
            "run `python scripts/vvh_campaign_v3.py --check`, `python scripts/vvh_campaign_v3_validate.py`, "
            "then `packwiz refresh` and `packwiz list`, followed by the client/live-server checks "
            "listed in `docs/vvh/UNRESOLVED.md`. Do not enable resets or sanctioned skirmishes "
            "until their runtime checks pass.\n",
        )

    print(json.dumps({
        "zip": str(args.zip_path),
        "file_count": len(entries),
        "chapters": len(current_chapters),
        "reward_tables": len(current_tables),
        "changed_chapters": len(changed_chapter_paths),
        "changed_reward_tables": len(changed_table_paths),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
