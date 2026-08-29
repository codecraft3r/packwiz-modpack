#!/usr/bin/env python3
"""One-way sync helper from workspace packwiz repository to local Prism Launcher instance.

Copies config/, kubejs/, and datapacks/ from the repository into the local
Prism Launcher instance directory. This never reads or pulls from the instance,
ensuring the git repository remains the untampered source of truth.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sync_to_instance() -> int:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        print("APPDATA environment variable not found.")
        return 1

    instance_dir = Path(appdata) / "PrismLauncher/instances/Poiesis Modded dev/minecraft"
    if not instance_dir.exists():
        print(f"Target instance directory not found: {instance_dir}")
        return 1

    sync_targets = ["config/ftbquests", "kubejs", "datapacks"]
    for rel_target in sync_targets:
        src = ROOT / rel_target
        dest = instance_dir / rel_target
        if src.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dest)
            print(f"[SYNC] {rel_target} -> {dest}")

    print("One-way sync completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(sync_to_instance())
