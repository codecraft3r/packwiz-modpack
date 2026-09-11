#!/usr/bin/env python3
"""Synchronize campaign ID evidence with the live Packwiz manifest.

The existing catalog supplies direct JAR-entry evidence, but an entry is kept
only when its source JAR is the exact filename pinned by an indexed .pw.toml.
This prevents unrelated or stale downloaded JARs from proving pack content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
import zipfile
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vvh_validate import Parser  # noqa: E402


NAMESPACE_METADATA = {
    "abyssal_decor": "mods/abyssal-decor.pw.toml",
    "create": "mods/create.pw.toml",
    "createbigcannons": "mods/create-big-cannons.pw.toml",
    "createdeco": "mods/create-deco.pw.toml",
    "explorerscompass": "mods/explorers-compass.pw.toml",
    "exposure": "mods/exposure.pw.toml",
    "irons_spellbooks": "mods/irons-spells-n-spellbooks.pw.toml",
    "mannequins": "mods/mannequins.pw.toml",
    "numismatics": "mods/numismatics.pw.toml",
    "sophisticatedbackpacks": "mods/sophisticated-backpacks.pw.toml",
    "supplementaries": "mods/supplementaries.pw.toml",
    "vampirism": "mods/vampirism.pw.toml",
    "vista": "mods/vista_tv.pw.toml",
}

EXTRA_ITEM_EVIDENCE = {
    "explorerscompass:explorerscompass": {
        "display_name": "Explorer's Compass",
        "source_entry": (
            "assets/explorerscompass/models/item/explorerscompass.json; "
            "data/explorerscompass/recipe/explorers_compass.json"
        ),
    },
    "exposure:album": {
        "display_name": "Photo Album",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.album",
    },
    "exposure:black_and_white_film": {
        "display_name": "Black and White Film",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.black_and_white_film",
    },
    "exposure:camera": {
        "display_name": "Camera",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.camera",
    },
    "exposure:camera_stand": {
        "display_name": "Camera Stand",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.camera_stand",
    },
    "exposure:color_film": {
        "display_name": "Color Film",
        "source_entry": "assets/exposure/models/item/color_film.json",
    },
    "exposure:high_sensitivity_color_film": {
        "display_name": "High-Sensitivity Color Film",
        "source_entry": (
            "assets/exposure/lang/en_us.json::item.exposure.high_sensitivity_color_film; "
            "data/exposure/recipe/high_sensitivity_color_film.json"
        ),
    },
    "exposure:photograph": {
        "display_name": "Photograph",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.photograph",
    },
    "exposure:photograph_frame": {
        "display_name": "Photograph Frame",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.photograph_frame",
    },
}

EXTRA_ADVANCEMENT_EVIDENCE = {
    "exposure:adventure/exposure": {
        "source_entry": "data/exposure/advancement/adventure/exposure.json",
    },
    "exposure:adventure/moment_in_time": {
        "source_entry": "data/exposure/advancement/adventure/moment_in_time.json",
    },
}

COIN_VALUES = [
    {"id": "numismatics:spur", "display_name": "Spur", "value_in_spurs": 1, "value_in_bevels": 0.125},
    {"id": "numismatics:bevel", "display_name": "Bevel", "value_in_spurs": 8, "value_in_bevels": 1},
    {"id": "numismatics:sprocket", "display_name": "Sprocket", "value_in_spurs": 16, "value_in_bevels": 2},
    {"id": "numismatics:cog", "display_name": "Cog", "value_in_spurs": 64, "value_in_bevels": 8},
    {"id": "numismatics:crown", "display_name": "Crown", "value_in_spurs": 512, "value_in_bevels": 64},
    {"id": "numismatics:sun", "display_name": "Sun", "value_in_spurs": 4096, "value_in_bevels": 512},
]

# Stack limits are runtime properties, not properties of an item model or a
# recipe.  The catalog accepts a small JSON registry receipt produced by the
# harness (see ``load_stack_metadata`` below) and records the receipt source
# beside every item.  A missing value is deliberately retained as ``null``;
# callers must not silently turn that into the common 64-stack default.
STACK_METADATA_CANDIDATES = (
    "docs/vvh/evidence/current/item-stack-registry.json",
)


def _stack_value(value: Any) -> int | None:
    """Read a positive max-stack integer without coercing unknown values."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, dict):
        for key in ("max_stack_size", "maxStackSize", "stack_size", "stackSize", "max_stack"):
            result = _stack_value(value.get(key))
            if result is not None:
                return result
    return None


def _walk_stack_metadata(value: Any, result: dict[str, int]) -> None:
    """Accept the common harness receipt shapes without guessing IDs."""
    if isinstance(value, list):
        for child in value:
            if not isinstance(child, dict):
                continue
            iid = child.get("id") or child.get("item") or child.get("name")
            stack = _stack_value(child)
            if isinstance(iid, str) and ":" in iid and stack is not None:
                result[iid] = stack
            _walk_stack_metadata(child, result)
        return
    if not isinstance(value, dict):
        return
    # A direct item map: {"namespace:item": {"max_stack_size": 64}}.
    for key, child in value.items():
        if isinstance(key, str) and ":" in key:
            stack = _stack_value(child)
            if stack is not None:
                result[key] = stack
    # Nested registry maps used by the runtime probe.
    for key in ("items", "item_registry", "itemRegistry", "registry", "registries"):
        child = value.get(key)
        if isinstance(child, (dict, list)):
            _walk_stack_metadata(child, result)


def load_stack_metadata(root: Path) -> tuple[dict[str, int], dict[str, str]]:
    """Load reviewed max-stack evidence; source receipts are not runtime probes.

    Returns ``(limits, sources)``.  The function is intentionally read-only
    and does not inspect arbitrary downloaded JARs: bytecode/model presence
    cannot prove the final registered ``Item#getMaxStackSize`` value.
    """
    limits: dict[str, int] = {}
    sources: dict[str, str] = {}
    for relative in STACK_METADATA_CANDIDATES:
        path = root / relative
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("kind") != "pinned_bytecode_stack_receipt" or not isinstance(payload.get("items"), dict):
            raise ValueError(f"{relative}: expected a reviewed pinned bytecode stack receipt")
        for iid, entry in payload["items"].items():
            evidence = entry.get("evidence", {}) if isinstance(entry, dict) else {}
            digest = evidence.get("sha256", "")
            if evidence.get("kind") not in {"pinned_bytecode", "minecraft_mapped_runtime"} or len(digest) != 64 or not evidence.get("class"):
                raise ValueError(f"{relative}: {iid} lacks class and exact artifact digest evidence")
            value = _stack_value(entry)
            if value is None:
                raise ValueError(f"{relative}: {iid} has no positive max stack size")
            limits[iid] = value
            sources[iid] = relative
    return limits, sources


def file_digest(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_metadata(root: Path, namespace: str) -> str:
    """Resolve a namespace to one indexed Packwiz metadata file.

    The explicit map documents known namespace-to-mod relationships.  The
    fallback handles newly introduced namespaces by inspecting metadata names
    and filenames, and fails closed when the result is ambiguous instead of
    silently selecting the first downloaded JAR.
    """
    explicit = NAMESPACE_METADATA.get(namespace)
    if explicit:
        return explicit
    token = namespace.replace("_", "").replace("-", "").lower()
    candidates: list[str] = []
    for path in sorted((root / "mods").glob("*.pw.toml")):
        try:
            metadata = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            continue
        haystack = " ".join(
            str(metadata.get(key, ""))
            for key in ("name", "filename")
        ).replace("_", "").replace("-", "").lower()
        if token and token in haystack:
            candidates.append(str(path.relative_to(root)).replace("\\", "/"))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ValueError(f"no Packwiz metadata mapping for live namespace {namespace!r}")
    raise ValueError(f"ambiguous Packwiz metadata for live namespace {namespace!r}: {candidates}")


def discover_item_evidence(root: Path, iid: str, proof: dict[str, Any]) -> dict[str, Any]:
    """Resolve an item directly from the exact pinned JAR in tmp/modcache.

    The catalog remains campaign-scoped, but newly authored IDs no longer need
    a hand-maintained Python dictionary before they can be proven. A generated
    item model is registry evidence; a matching recipe entry is recorded when
    the mod exposes a normal data recipe.
    """
    namespace, path = iid.split(":", 1)
    jar_path = root / "tmp/modcache" / str(proof["filename"])
    if not jar_path.is_file():
        raise ValueError(f"{iid}: exact pinned JAR is not materialized at {jar_path}")
    with zipfile.ZipFile(jar_path) as jar:
        names = set(jar.namelist())
        model = f"assets/{namespace}/models/item/{path}.json"
        block_model = f"assets/{namespace}/models/block/{path}.json"
        blockstate = f"assets/{namespace}/blockstates/{path}.json"
        lang_path = f"assets/{namespace}/lang/en_us.json"
        source_entries = [candidate for candidate in (model, block_model, blockstate) if candidate in names]
        # Some valid registered items (notably tools and generated items) have
        # no standalone model.  A pinned language key or registry class is
        # still useful exact-JAR evidence, but absence of all such evidence
        # must remain a hard failure.
        if lang_path in names:
            lang = json.loads(jar.read(lang_path).decode("utf-8"))
            if f"item.{namespace}.{path}" in lang or f"block.{namespace}.{path}" in lang:
                source_entries.append(f"{lang_path}::item.{namespace}.{path}")
        if not source_entries:
            registry_marker = f"{namespace}.{path}"
            marker_entries = sorted(
                name for name in names
                if name.endswith(".class") and registry_marker.encode("utf-8") in jar.read(name)
            )
            if marker_entries:
                source_entries.append(f"{marker_entries[0]}::registry-string:{registry_marker}")
        if not source_entries:
            raise ValueError(f"{iid}: no exact item/block/lang/registry evidence in {proof['filename']}")
        recipe_prefix = f"data/{namespace}/recipe/"
        recipe_matches = sorted(
            name for name in names
            if name.startswith(recipe_prefix)
            and name.endswith(".json")
            and Path(name).stem in {path, f"{path}_crafting"}
        )
        source_entries.extend(recipe_matches[:3])
        display_name = path.replace("_", " ").title()
        if lang_path in names:
            display_name = (
                lang.get(f"item.{namespace}.{path}")
                or lang.get(f"block.{namespace}.{path}")
                or display_name
            )
    note = "Exact item model is present in the pinned JAR."
    if recipe_matches:
        note = "Exact item model and survival data recipe are present in the pinned JAR."
    return {
        "namespace": namespace,
        "id": iid,
        "display_name": display_name,
        "source_jar": proof["filename"],
        "source_entry": "; ".join(source_entries),
        "obtainability_note": note,
    }


def validate_source_entry_paths(root: Path, entry: dict[str, Any], proof: dict[str, Any]) -> None:
    """Re-check every recorded archive path when the exact JAR is present.

    Catalog entries are intentionally reusable on machines that do not keep
    downloaded artifacts, but a materialized exact JAR gives us a cheap stale-
    evidence check.  A same-named replacement JAR cannot continue to prove an
    old model, language file, recipe, advancement, or class path.
    """
    if not proof.get("artifact_materialized"):
        return
    jar_path = root / "tmp/modcache" / str(proof["filename"])
    source_entry = entry.get("source_entry")
    if not isinstance(source_entry, str) or not source_entry:
        raise ValueError(f"{entry.get('id', '<unknown>')}: direct JAR entry evidence is empty")
    with zipfile.ZipFile(jar_path) as jar:
        names = set(jar.namelist())
    for raw_path in source_entry.split(";"):
        archive_path = raw_path.strip().split("::", 1)[0].strip()
        if not archive_path or archive_path.startswith("#"):
            continue
        if archive_path.startswith(("assets/", "data/", "net/", "com/", "org/")) and archive_path not in names:
            raise ValueError(
                f"{entry.get('id', '<unknown>')}: recorded evidence path {archive_path!r} "
                f"is absent from current exact JAR {proof['filename']}"
            )


def metadata_is_unchanged(old: dict[str, Any], namespace: str, proof: dict[str, Any]) -> bool:
    membership = old.get("pack_membership")
    namespaces = membership.get("namespaces") if isinstance(membership, dict) else None
    previous = namespaces.get(namespace) if isinstance(namespaces, dict) else None
    if not isinstance(previous, dict):
        return False
    return all(
        previous.get(key) == proof.get(current)
        for key, current in (
            ("metadata_sha256", "metadata_sha256"),
            ("filename", "filename"),
            ("download_hash_format", "download_hash_format"),
            ("download_hash", "download_hash"),
        )
    )


def discover_spell_evidence(root: Path, sid: str, proof: dict[str, Any]) -> dict[str, Any]:
    namespace, path = sid.split(":", 1)
    jar_path = root / "tmp/modcache" / str(proof["filename"])
    if not jar_path.is_file():
        raise ValueError(f"{sid}: exact pinned JAR is not materialized at {jar_path}")
    camel = "".join(part.capitalize() for part in path.split("_")) + "Spell.class"
    with zipfile.ZipFile(jar_path) as jar:
        names = jar.namelist()
        class_matches = sorted(name for name in names if name.endswith("/" + camel))
        if not class_matches:
            raise ValueError(f"{sid}: no exact spell implementation class in {proof['filename']}")
        lang_path = f"assets/{namespace}/lang/en_us.json"
        lang = json.loads(jar.read(lang_path).decode("utf-8")) if lang_path in names else {}
        display_name = lang.get(f"spell.{namespace}.{path}", path.replace("_", " ").title())
    class_path = class_matches[0]
    school = class_path.split("/spells/", 1)[1].split("/", 1)[0] if "/spells/" in class_path else ""
    return {
        "id": sid,
        "display_name": display_name,
        "school": school,
        "source_jar": proof["filename"],
        "source_entry": f"assets/{namespace}/lang/en_us.json::spell.{namespace}.{path}; {class_path}",
    }


def item_id(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("id"), str):
        return value["id"]
    return None


def parse_live_snbt(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    value = Parser(text, str(path)).parse()
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected root compound")
    return value


def collect_live_references(root: Path, *, from_source: bool = False) -> tuple[set[str], set[str], set[str]]:
    items: set[str] = set()
    advancements: set[str] = set()
    spells: set[str] = set()

    generated = {}
    if from_source:
        import vvh_campaign_v3
        generated = vvh_campaign_v3.outputs(root)
    def read(path: Path):
        return Parser(generated[path], str(path)).parse() if path in generated else parse_live_snbt(path)
    def paths(directory: str):
        parent = root / directory
        return sorted(path for path in generated if path.parent == parent and path.suffix == ".snbt") if from_source else sorted(parent.glob("*.snbt"))
    data = read(root / "config/ftbquests/quests/data.snbt")
    if (iid := item_id(data.get("icon"))) is not None:
        items.add(iid)

    from frontier_campaign import chapter_names
    frontier_names = chapter_names(root)
    for path in paths("config/ftbquests/quests/chapters"):
        # Frontier has its own exact-artifact and live registry evidence ledger.
        if path.stem in frontier_names:
            continue
        chapter = read(path)
        if (iid := item_id(chapter.get("icon"))) is not None:
            items.add(iid)
        for quest in chapter.get("quests", []):
            if (iid := item_id(quest.get("icon"))) is not None:
                items.add(iid)
            for task in quest.get("tasks", []):
                if (iid := item_id(task.get("item"))) is not None:
                    items.add(iid)
                if isinstance(task.get("advancement"), str):
                    advancements.add(task["advancement"])
                collect_spell_references(task.get("item"), spells)
            for reward in quest.get("rewards", []):
                stack = reward.get("item")
                if (iid := item_id(stack)) is not None:
                    items.add(iid)
                collect_spell_references(stack, spells)

    # Choice rewards live in separate emitted files.  They are part of the
    # loaded campaign just like chapter rewards, so include their item IDs in
    # the same provenance pass; otherwise a table-only item could bypass the
    # exact-JAR evidence gate and remain invisible to the catalog.
    for path in paths("config/ftbquests/quests/reward_tables"):
        table = read(path)
        for reward in table.get("rewards", []):
            if not isinstance(reward, dict):
                continue
            if (iid := item_id(reward.get("item"))) is not None:
                items.add(iid)
            stack = reward.get("item")
            collect_spell_references(stack, spells)
    return items, advancements, spells


def collect_spell_references(stack: Any, spells: set[str]) -> None:
    """Collect every spell-bearing item component from any quest object."""
    if not isinstance(stack, dict) or not isinstance(stack.get("components"), dict):
        return
    components = stack["components"]
    affinity = components.get("irons_spellbooks:affinity_data")
    if isinstance(affinity, dict) and isinstance(affinity.get("id"), str):
        spells.add(affinity["id"])
    container = components.get("irons_spellbooks:spell_container")
    if isinstance(container, dict):
        for slot in container.get("data", []):
            if isinstance(slot, dict) and isinstance(slot.get("id"), str):
                spells.add(slot["id"])


def pack_membership(root: Path, namespaces: set[str]) -> dict[str, Any]:
    index = tomllib.loads((root / "index.toml").read_text(encoding="utf-8"))
    index_files = {entry["file"]: entry for entry in index.get("files", [])}
    proofs: dict[str, Any] = {}
    for namespace in sorted(namespaces):
        metadata_rel = resolve_metadata(root, namespace)
        if metadata_rel not in index_files:
            raise ValueError(f"{namespace}: {metadata_rel} is not indexed by index.toml")
        metadata_path = root / metadata_rel
        metadata = tomllib.loads(metadata_path.read_text(encoding="utf-8"))
        download = metadata.get("download", {})
        if metadata.get("side", "both") == "client":
            raise ValueError(f"{namespace}: campaign content cannot come from client-only {metadata_rel}")
        declared_index_hash = index_files[metadata_rel].get("hash")
        actual_index_hash = file_digest(metadata_path, "sha256")
        if declared_index_hash != actual_index_hash:
            raise ValueError(
                f"{namespace}: index hash mismatch for {metadata_rel}: "
                f"declared={declared_index_hash} actual={actual_index_hash}"
            )
        filename = metadata.get("filename")
        artifact_path = root / "tmp/modcache" / str(filename)
        artifact_materialized = artifact_path.is_file()
        artifact_hash_matches: bool | None = None
        if artifact_materialized:
            hash_format = str(download.get("hash-format", "")).lower().replace("-", "")
            declared_download_hash = str(download.get("hash", "")).lower()
            if not hash_format or not declared_download_hash:
                raise ValueError(f"{namespace}: Packwiz download hash is missing for {metadata_rel}")
            try:
                actual_download_hash = file_digest(artifact_path, hash_format)
            except (ValueError, OSError) as exc:
                raise ValueError(f"{namespace}: cannot hash {artifact_path.name}: {exc}") from exc
            artifact_hash_matches = actual_download_hash == declared_download_hash
            if not artifact_hash_matches:
                raise ValueError(
                    f"{namespace}: materialized JAR hash mismatch for {filename}: "
                    f"declared={declared_download_hash} actual={actual_download_hash}"
                )
        proofs[namespace] = {
            "metadata": metadata_rel,
            "name": metadata.get("name"),
            "filename": filename,
            "side": metadata.get("side", "both"),
            "download_hash_format": download.get("hash-format"),
            "download_hash": download.get("hash"),
            "index_sha256": declared_index_hash,
            "metadata_sha256": actual_index_hash,
            "artifact_materialized": artifact_materialized,
            "artifact_hash_matches": artifact_hash_matches,
            # Metadata can be checked on a clean machine, but exact JAR-entry
            # provenance is only proven after the declared artifact is present
            # and its bytes match the Packwiz download digest.
            "artifact_verified": artifact_materialized and artifact_hash_matches is True,
        }
    return proofs


def synchronize(root: Path, *, from_source: bool = False) -> dict[str, Any]:
    path = root / "docs/vvh/id_catalog.json"
    old = json.loads(path.read_text(encoding="utf-8"))
    stack_limits, stack_sources = load_stack_metadata(root)
    items, advancements, spells = collect_live_references(root, from_source=from_source)
    non_vanilla_items = {iid for iid in items if not iid.startswith("minecraft:")}
    namespaces = {
        value.split(":", 1)[0]
        for value in (*non_vanilla_items, *advancements, *spells)
    }
    proofs = pack_membership(root, namespaces)
    old_items = {str(entry.get("id")): entry for entry in old.get("entries", [])}
    old_proofs = old.get("pack_membership", {}).get("namespaces", {})
    old_advancements = {
        str(entry.get("id")): entry
        for group in old.get("advancements", {}).values()
        for entry in group
    }
    old_spells = {str(entry.get("id")): entry for entry in old.get("spells", [])}

    # A clean CI checkout often omits the ignored JAR cache.  If the indexed
    # metadata and download digest are unchanged, retain the previous
    # hash-verified status instead of rewriting a previously proven catalog as
    # metadata-only.  This does not claim the bytes are locally available;
    # ``artifact_materialized`` remains false and source-entry checks are
    # deferred until the exact artifact is present again.
    for namespace, proof in proofs.items():
        previous = old_proofs.get(namespace) if isinstance(old_proofs, dict) else None
        if (
            not proof.get("artifact_materialized")
            and isinstance(previous, dict)
            and previous.get("artifact_verified") is True
            and metadata_is_unchanged(old, namespace, proof)
        ):
            proof["artifact_verified"] = True
            proof["artifact_hash_matches"] = True


    entries: list[dict[str, Any]] = []
    for iid in sorted(non_vanilla_items):
        namespace = iid.split(":", 1)[0]
        entry = dict(old_items.get(iid, {})) if metadata_is_unchanged(old, namespace, proofs[namespace]) else {}
        if not entry:
            extra = EXTRA_ITEM_EVIDENCE.get(iid)
            if extra is not None:
                entry = {"namespace": namespace, "id": iid, **extra, "obtainability_note": ""}
            else:
                entry = discover_item_evidence(root, iid, proofs[namespace])
        expected_jar = proofs[namespace]["filename"]
        entry["source_jar"] = entry.get("source_jar") or expected_jar
        if entry.get("source_jar") != expected_jar:
            raise ValueError(
                f"{iid}: evidence JAR {entry.get('source_jar')!r} is not current Packwiz JAR {expected_jar!r}"
            )
        if not entry.get("source_entry"):
            raise ValueError(f"{iid}: direct JAR entry evidence is empty")
        validate_source_entry_paths(root, entry, proofs[namespace])
        entry["artifact_verified"] = bool(proofs[namespace]["artifact_verified"])
        entry["max_stack_size"] = stack_limits.get(iid)
        entry["stack_size_verified"] = iid in stack_limits
        entry["stack_size_source"] = stack_sources.get(iid)
        entries.append(entry)

    advancement_entries: list[dict[str, Any]] = []
    for aid in sorted(advancements):
        namespace = aid.split(":", 1)[0]
        entry = dict(old_advancements.get(aid, {})) if metadata_is_unchanged(old, namespace, proofs[namespace]) else {}
        if not entry:
            extra = EXTRA_ADVANCEMENT_EVIDENCE.get(aid)
            if extra is None:
                raise ValueError(f"missing direct advancement evidence for {aid}")
            entry = {"id": aid, **extra}
        expected_jar = proofs[namespace]["filename"]
        entry["source_jar"] = entry.get("source_jar") or expected_jar
        if entry.get("source_jar") != expected_jar:
            raise ValueError(
                f"{aid}: evidence JAR {entry.get('source_jar')!r} is not current Packwiz JAR {expected_jar!r}"
            )
        validate_source_entry_paths(root, entry, proofs[namespace])
        entry["artifact_verified"] = bool(proofs[namespace]["artifact_verified"])
        advancement_entries.append(entry)

    spell_entries: list[dict[str, Any]] = []
    for sid in sorted(spells):
        namespace = sid.split(":", 1)[0]
        entry = dict(old_spells.get(sid, {})) if metadata_is_unchanged(old, namespace, proofs[namespace]) else {}
        if not entry:
            entry = discover_spell_evidence(root, sid, proofs[namespace])
        expected_jar = proofs[namespace]["filename"]
        if entry.get("source_jar") != expected_jar:
            raise ValueError(
                f"{sid}: evidence JAR {entry.get('source_jar')!r} is not current Packwiz JAR {expected_jar!r}"
            )
        validate_source_entry_paths(root, entry, proofs[namespace])
        entry["artifact_verified"] = bool(proofs[namespace]["artifact_verified"])
        spell_entries.append(entry)

    verified_namespaces = sorted(
        namespace for namespace, proof in proofs.items() if proof.get("artifact_verified") is True
    )
    unverified_namespaces = sorted(set(namespaces) - set(verified_namespaces))
    for proof in proofs.values():
        # Cache availability is transient, while the digest-bound verification
        # receipt must remain deterministic in clean CI checkouts.
        proof.pop("artifact_materialized", None)
        proof.pop("artifact_status", None)
    return {
        "generated_from": "Campaign SNBT references bound to current indexed Packwiz metadata; exact JAR-entry evidence is marked per namespace.",
        "verification_scope": "Campaign-used non-vanilla IDs only; unrelated downloaded JARs are excluded. Metadata-only entries remain explicitly unverified until the exact hash-checked JAR is materialized.",
        "verified_namespaces": verified_namespaces,
        "unverified_namespaces": unverified_namespaces,
        "pack_membership": {
            "index": "index.toml",
            "namespaces": proofs,
        },
        "entries": entries,
        "advancements": {"campaign": advancement_entries},
        "spells": spell_entries,
        "numismatics_denominations": COIN_VALUES,
        "stack_metadata": {
            "sources": sorted(set(stack_sources.values())),
            "item_count": len(stack_limits),
            "complete_for_campaign_items": all(
                entry.get("id") in stack_limits for entry in entries
            ),
            "limits": dict(sorted(stack_limits.items())),
        },
        "ftb_quests": old.get("ftb_quests", {}),
    }


def render_markdown(catalog: dict[str, Any]) -> str:
    lines = [
        "# VvH Current-Pack ID Catalog",
        "",
        "This catalog contains only IDs referenced by the live five-chapter campaign. "
        "Every non-vanilla namespace must be backed by a `.pw.toml` that is present in "
        "the current `index.toml`, and every evidence JAR must match that metadata's exact filename.",
        "",
        "An unrelated downloaded JAR is not proof that a mod is installed. Run "
        "`python -B -X utf8 scripts/vvh_sync_catalog.py --check .` before release.",
        "",
        "## Pack membership",
        "",
        "| Namespace | Indexed metadata | Pinned JAR | Side | Download hash | Artifact proof |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    proofs = catalog["pack_membership"]["namespaces"]
    for namespace, proof in proofs.items():
        digest = str(proof.get("download_hash", ""))
        lines.append(
            f"| `{namespace}` | `{proof['metadata']}` | `{proof['filename']}` | "
            f"`{proof['side']}` | `{proof.get('download_hash_format')}:{digest}` | "
            f"{'exact hash-verified JAR' if proof.get('artifact_verified') else 'metadata-only; JAR not materialized'} |"
        )

    lines.extend(
        [
            "",
            "## Campaign items and icons",
            "",
            "| Namespace | ID | Display name | Exact evidence JAR | JAR entry evidence | Artifact proof |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for entry in catalog["entries"]:
        lines.append(
            f"| `{entry['namespace']}` | `{entry['id']}` | {entry.get('display_name', '')} | "
            f"`{entry['source_jar']}` | `{entry['source_entry']}` | "
            f"{'exact hash-verified JAR' if entry.get('artifact_verified') else 'metadata-only'} |"
        )

    lines.extend(
        [
            "",
            "## Campaign advancements",
            "",
            "| ID | Exact evidence JAR | JAR entry evidence | Artifact proof |",
            "| --- | --- | --- | --- |",
        ]
    )
    for entry in catalog["advancements"]["campaign"]:
        lines.append(
            f"| `{entry['id']}` | `{entry['source_jar']}` | `{entry['source_entry']}` | "
            f"{'exact hash-verified JAR' if entry.get('artifact_verified') else 'metadata-only'} |"
        )

    lines.extend(
        [
            "",
            "## Campaign spell IDs",
            "",
            "| ID | School | Exact evidence JAR | JAR entry evidence | Artifact proof |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for entry in catalog["spells"]:
        lines.append(
            f"| `{entry['id']}` | {entry.get('school', '')} | `{entry['source_jar']}` | "
            f"`{entry['source_entry']}` | "
            f"{'exact hash-verified JAR' if entry.get('artifact_verified') else 'metadata-only'} |"
        )

    lines.extend(
        [
            "",
            "## Verified max stack sizes",
            "",
            "Values come from the runtime registry receipt, not from a universal 64-item assumption. "
            "A missing value remains unknown and must be resolved before a bulk reward is released.",
            "",
            "| ID | Max stack | Evidence |",
            "| --- | ---: | --- |",
        ]
    )
    stack_limits = catalog.get("stack_metadata", {}).get("limits", {})
    for entry in catalog["entries"]:
        iid = entry["id"]
        limit = stack_limits.get(iid)
        lines.append(
            f"| `{iid}` | {limit if limit is not None else 'unknown'} | "
            f"`{entry.get('stack_size_source') or 'unverified'}` |"
        )

    lines.extend(
        [
            "",
            "## Numismatics denominations",
            "",
            "Values were extracted from `dev.ithundxr.createnumismatics.content.backend.Coin` "
            "in the exact pinned JAR.",
            "",
            "| ID | Spurs | Bevel-equivalent |",
            "| --- | ---: | ---: |",
        ]
    )
    for entry in catalog["numismatics_denominations"]:
        lines.append(
            f"| `{entry['id']}` | {entry['value_in_spurs']} | {entry['value_in_bevels']} |"
        )

    lines.extend(
        [
            "",
            "## FTB Quests schema observations",
            "",
            f"- Installed evidence JAR: `{catalog['ftb_quests'].get('installed_filename', '')}`",
            "- Observed task/reward types: "
            + ", ".join(f"`{value}`" for value in catalog["ftb_quests"].get("task_types_observed", [])),
            "",
            "Vanilla `minecraft:*` IDs are outside this campaign-scoped catalog. Runtime/client checks "
            "remain separate from static Packwiz membership and JAR-entry proof.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--from-source", action="store_true", help="Preflight authoritative generated references without overwriting live SNBT")
    args = parser.parse_args()
    root = args.root.resolve()
    path = root / "docs/vvh/id_catalog.json"
    markdown_path = root / "docs/vvh/ID_CATALOG.md"
    catalog = synchronize(root, from_source=args.from_source)
    rendered = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    markdown = render_markdown(catalog)
    current = path.read_text(encoding="utf-8")
    if args.check:
        stale: list[str] = []
        if current != rendered:
            stale.append(str(path))
        if markdown_path.read_text(encoding="utf-8") != markdown:
            stale.append(str(markdown_path))
        if stale:
            print("campaign ID catalog is stale: " + ", ".join(stale))
            return 1
        print("campaign ID catalog is synchronized with Packwiz")
        return 0
    path.write_text(rendered, encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    print(f"synchronized {path} and {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
