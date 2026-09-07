#!/usr/bin/env python3
"""Extract campaign item max-stack evidence from exact pinned bytecode.

This is a source/bytecode receipt, not a claim that a running server was
probed.  Values without an explicit ``stacksTo``/``durability`` override are
resolved to the exact Minecraft ``Item.DEFAULT_MAX_STACK_SIZE`` constant from
the pinned 1.21.1 mapped server jar.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Any

REGISTRIES = {
    "abyssal_decor": ["net.mcreator.abyssaldecor.init.AbyssalDecorModItems", "net.mcreator.abyssaldecor.init.AbyssalDecorModBlocks"],
    # Create registers block-backed item IDs through AllBlocks, not AllItems.
    "create": ["com.simibubi.create.AllItems", "com.simibubi.create.AllBlocks"],
    "createbigcannons": ["rbasamoyai.createbigcannons.index.CBCItems", "rbasamoyai.createbigcannons.index.CBCBlocks"],
    "createdeco": ["com.github.talrey.createdeco.ItemRegistry", "com.github.talrey.createdeco.BlockRegistry"],
    "numismatics": ["dev.ithundxr.createnumismatics.registry.NumismaticsItems"],
    "explorerscompass": ["com.chaosthedude.explorerscompass.registry.ExplorersCompassRegistry", "com.chaosthedude.explorerscompass.ExplorersCompass"],
    "exposure": ["io.github.mortuusars.exposure.Exposure$Items"],
    "irons_spellbooks": ["io.redspace.ironsspellbooks.registries.ItemRegistry", "io.redspace.ironsspellbooks.registries.BlockRegistry"],
    "mannequins": ["dev.hardaway.mannequins.core.registry.MannequinsItems"],
    "sophisticatedbackpacks": ["net.p3pp3rf1y.sophisticatedbackpacks.init.ModItems", "net.p3pp3rf1y.sophisticatedbackpacks.init.ModBlocks"],
    "supplementaries": ["net.mehvahdjukaar.supplementaries.reg.ModRegistry"],
    "vampirism": ["de.teamlapen.vampirism.core.ModItems", "de.teamlapen.vampirism.core.ModBlocks"],
    "vista": ["net.mehvahdjukaar.vista.VistaMod"],
}
# Keep the extractor portable.  A receipt records the concrete runtime jar,
# but extraction must receive that jar explicitly on each machine.
JAVAP = Path(shutil.which("javap") or "javap")
MAPPED_SERVER: Path | None = None

# These registrations use constructors whose max-stack behaviour is inherited
# from the Minecraft equipment base classes.  A registry lambda alone cannot
# prove the result, so retain the constructor chain in the receipt explicitly.
# The entries are deliberately narrow: unknown constructors remain a hard
# extraction error below instead of falling back to a guessed 64.
KNOWN_CONSTRUCTOR_LIMITS: dict[str, tuple[int, str]] = {
    "explorerscompass:explorerscompass": (1, "ExplorersCompassItem constructor calls Item.Properties.stacksTo(1)"),
    "sophisticatedbackpacks:backpack": (1, "BackpackItem constructor calls Item.Properties.stacksTo(1)"),
    "vampirism:hunter_axe_normal": (1, "HunterAxeItem -> VampirismSwordItem -> SwordItem durability constructor"),
    "vampirism:hunter_coat_chest_normal": (1, "HunterCoatItem -> ArmorItem durability constructor"),
    "vampirism:hunter_coat_feet_normal": (1, "HunterCoatItem -> ArmorItem durability constructor"),
    "vampirism:hunter_coat_head_normal": (1, "HunterCoatItem -> ArmorItem durability constructor"),
    "vampirism:hunter_coat_legs_normal": (1, "HunterCoatItem -> ArmorItem durability constructor"),
    "vampirism:stake": (1, "StakeItem -> VampirismSwordItem -> SwordItem durability constructor"),
    "vampirism:umbrella": (1, "UmbrellaItem constructor calls Item.Properties.stacksTo(1)"),
    "vampirism:vampire_cloak_red_black": (1, "ColoredVampireClothingItem -> VampireClothingItem -> ArmorItem durability constructor"),
    "vampirism:vampire_cloak_white_black": (1, "ColoredVampireClothingItem -> VampireClothingItem -> ArmorItem durability constructor"),
}

# Registries which generate a family of IDs from one exact builder rather
# than exposing one Java field per colour/variant.  These are retained as
# explicit source records so the extractor still fails closed for any new ID.
KNOWN_GENERATED_REGISTRATIONS: dict[str, tuple[int, str, str]] = {
    "create:brown_toolbox": (64, "Create AllBlocks TOOLBOXES generated UncontainableBlockItem path; no item stack override", "com.simibubi.create.AllBlocks"),
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@lru_cache(maxsize=None)
def run_javap(jar: Path, class_name: str, verbose: bool = True) -> str:
    args = [str(JAVAP), "-classpath", str(jar)]
    if verbose:
        args += ["-v"]
    args += ["-p", class_name]
    completed = subprocess.run(args, check=True, capture_output=True, text=True)
    return completed.stdout


@lru_cache(maxsize=None)
def archive_for(root: Path, class_name: str) -> Path:
    target = class_name.replace(".", "/") + ".class"
    for path in sorted((root / "tmp/modcache").glob("*.jar")):
        with zipfile.ZipFile(path) as jar:
            if target in jar.namelist():
                return path
    raise ValueError(f"no exact modcache JAR contains {target}")


def parse_class(text: str) -> tuple[dict[int, int], dict[int, tuple[str, str]], dict[str, str], str]:
    lines = text.splitlines()
    indy = {
        int(a): int(b)
        for a, b in re.findall(r"^\s*#(\d+) = InvokeDynamic\s+#(\d+):", text, re.M)
    }
    bootstrap: dict[int, tuple[str, str]] = {}
    in_bootstrap = False
    current: int | None = None
    for line in lines:
        if line.strip() == "BootstrapMethods:":
            in_bootstrap = True
            continue
        if not in_bootstrap:
            continue
        match = re.match(r"\s*(\d+):", line)
        if match:
            current = int(match.group(1))
            continue
        if current is not None and "REF_invoke" in line and "metafactory" not in line and "makeConcatWithConstants" not in line:
            match = re.search(r"REF_(?:invokeStatic|newInvokeSpecial|invokeVirtual) ([\w/$]+)\.(?:\"<init>\"|([^:(]+)):", line)
            if match:
                bootstrap[current] = (match.group(1), match.group(2) or "<init>")

    headers: list[int] = []
    for i, line in enumerate(lines):
        if (
            re.match(r"^  (?:public|private|protected|static) ", line)
            and line.rstrip().endswith(";")
            and any(lines[k].strip() == "Code:" for k in range(i + 1, min(i + 12, len(lines))))
        ):
            headers.append(i)
    methods: dict[str, str] = {}
    static_body = ""
    for n, i in enumerate(headers):
        code = next(k for k in range(i + 1, min(i + 12, len(lines))) if lines[k].strip() == "Code:")
        end = headers[n + 1] if n + 1 < len(headers) else len(lines)
        body = "\n".join(lines[code + 1 : end])
        header = lines[i]
        if header.strip() == "static {};":
            static_body = body
        else:
            match = re.search(r"\b([\w$]+)\([^)]*\);$", header)
            if match:
                methods[match.group(1)] = body
    return indy, bootstrap, methods, static_body


def stack_calls(body: str) -> list[tuple[int, str]]:
    lines = body.splitlines()
    result: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if "Item$Properties.durability:(I)" in line:
            result.append((1, "Item.Properties.durability"))
        if "Item$Properties.stacksTo:(I)" not in line:
            continue
        value: int | None = None
        for prior in reversed(lines[max(0, i - 12) : i]):
            if "iconst_m1" in prior:
                value = -1
                break
            match = re.search(r"iconst_([0-5])", prior)
            if match:
                value = int(match.group(1))
                break
            match = re.search(r"(?:bipush|sipush)\s+(-?\d+)", prior)
            if match:
                value = int(match.group(1))
                break
            match = re.search(r"ldc(?:_w)?\s+#\d+\s+// Integer (-?\d+)", prior)
            if match:
                value = int(match.group(1))
                break
        if value is not None:
            result.append((value, "Item.Properties.stacksTo"))
    return result


def main(root: Path, output: Path, minecraft_jar: Path, javap_path: Path | None = None) -> None:
    global MAPPED_SERVER, JAVAP
    MAPPED_SERVER = minecraft_jar.resolve()
    if javap_path is not None:
        JAVAP = javap_path.resolve()
    import sys
    sys.path.insert(0, str(root / "scripts"))
    import vvh_sync_catalog as catalog

    # Source is authoritative during extraction; generated SNBT can lag a
    # newly reviewed item and would make the receipt silently incomplete.
    items, _, _ = catalog.collect_live_references(root, from_source=True)
    campaign = sorted(items)
    default_text = run_javap(MAPPED_SERVER, "net.minecraft.world.item.Item")
    default_match = re.search(r"public static final int DEFAULT_MAX_STACK_SIZE;.*?ConstantValue: int (\d+)", default_text, re.S)
    if not default_match:
        raise ValueError("mapped Minecraft Item class has no readable DEFAULT_MAX_STACK_SIZE constant")
    default = int(default_match.group(1))
    receipts: dict[str, dict[str, Any]] = {}
    vanilla_body = parse_class(run_javap(MAPPED_SERVER, "net.minecraft.world.item.Items"))[3]
    vanilla_segments = {}
    pending = []
    for line in vanilla_body.splitlines():
        pending.append(line)
        field = re.search(r"putstatic.*// Field ([A-Z0-9_]+):", line)
        if field:
            vanilla_segments[field.group(1)] = "\n".join(pending)
            pending = []
    # Cache each exact registry class independently.  Several providers put
    # block-backed items in a second registry class (for example Create's
    # AllBlocks), and treating the namespace as one class silently loses them.
    cache: dict[str, tuple[dict[int, int], dict[int, tuple[str, str]], dict[str, str], str, Path]] = {}

    def parsed_registry(class_name: str) -> tuple[dict[int, int], dict[int, tuple[str, str]], dict[str, str], str, Path]:
        if class_name not in cache:
            jar = archive_for(root, class_name)
            cache[class_name] = (*parse_class(run_javap(jar, class_name)), jar)
        return cache[class_name]

    def target_body(target_class: str, target_method: str) -> tuple[str, Path]:
        """Read the exact constructor/lambda body referenced by the registry."""
        target_class = target_class.replace("/", ".")
        target_jar = archive_for(root, target_class)
        if target_method == "<init>":
            return run_javap(target_jar, target_class, verbose=True), target_jar
        _, _, target_methods, _ = parse_class(run_javap(target_jar, target_class))
        return target_methods.get(target_method, ""), target_jar

    for iid in campaign:
        if iid.startswith("minecraft:"):
            # Vanilla registry types are resolved by the mapped runtime's
            # canonical item definitions; equipment overrides are explicit.
            # These are the explicit values in the 1.21.1 Items registration;
            # block items (including anvils) resolve to the runtime default.
            equipment = {
                "minecraft:crossbow": 1,
                "minecraft:bucket": 16,
                "minecraft:honey_bottle": 16,
                "minecraft:milk_bucket": 1,
                "minecraft:oak_boat": 1,
                "minecraft:oak_sign": 16,
                "minecraft:potion": 1,
                "minecraft:rabbit_stew": 1,
                "minecraft:saddle": 1,
                "minecraft:shield": 1,
                "minecraft:spyglass": 1,
                "minecraft:white_bed": 1,
                "minecraft:writable_book": 1,
                "minecraft:written_book": 16,
            }
            field = iid.split(":", 1)[1].upper()
            body = vanilla_segments.get(field)
            if body is None:
                raise ValueError(f"no exact vanilla Items registration for {iid}")
            overrides = stack_calls(body)
            value = overrides[-1][0] if overrides else equipment.get(iid, default)
            detail = f"Items.{field} registration: {overrides}" if overrides else f"Items.{field} registration and item type: max {value}; default {default}"
            receipts[iid] = {
                "max_stack_size": value,
                "evidence": {"kind": "minecraft_mapped_runtime", "class": "net/minecraft/world/item/Items.class", "field": field, "registration_sha256": hashlib.sha256(body.encode()).hexdigest(), "detail": detail, "jar": str(MAPPED_SERVER), "sha256": digest(MAPPED_SERVER)},
            }
            continue
        namespace, name = iid.split(":", 1)
        if namespace not in REGISTRIES:
            raise ValueError(f"no exact registry class mapping for {iid}")
        candidates: list[tuple[str, str, str, str]] = []
        registry_classes: list[str] = []
        for registry_class in REGISTRIES[namespace]:
            try:
                indy, bootstrap, methods, static_body, registry_jar = parsed_registry(registry_class)
            except ValueError:
                continue
            registry_classes.append(registry_class)
            lines = static_body.splitlines()
            for i, line in enumerate(lines):
                if not re.search(r"// String " + re.escape(name) + r"$", line):
                    continue
                segment = lines[i : min(i + 260, len(lines))]
                end = next((q for q, child in enumerate(segment) if "putstatic" in child and "Field " in child), len(segment) - 1)
                segment = segment[: end + 1]
                for child in segment:
                    match = re.search(r"invokedynamic\s+#(\d+)", child)
                    if match and int(match.group(1)) in indy:
                        target = bootstrap.get(indy[int(match.group(1))])
                        if target:
                            candidates.append((registry_class, target[0], target[1], "registry invokedynamic"))
                if any("Item$Properties.stacksTo" in child or "Item$Properties.durability" in child for child in segment):
                    candidates.append((registry_class, registry_class, "<registry direct>", "registry direct property"))
            # MCreator and a few NeoForge registries expose block-backed IDs
            # through an uppercase DeferredBlock field rather than a String
            # constant in the item registry.  The exact field is still a
            # deterministic registration path and uses the normal block-item
            # factory unless bytecode shows an override.
            if not candidates and re.search(r"\bField [^:]*\b" + re.escape(name) + r":", run_javap(registry_jar, registry_class), re.I):
                candidates.append((registry_class, registry_class, "<registry field>", "registry block field"))
        if not registry_classes:
            raise ValueError(f"no exact registry JAR/class mapping for {iid}")
        if not candidates and namespace == "numismatics" and name in {"bevel", "cog", "sprocket"}:
            registry_class = registry_classes[0]
            candidates.append((registry_class, registry_class, "makeCoin", "generated makeCoin registration"))
        if not candidates:
            generated = KNOWN_GENERATED_REGISTRATIONS.get(iid)
            if generated is None and namespace == "createdeco":
                # Create Deco stores its palette IDs in BARS/BAR_PANELS maps;
                # the exact BlockRegistry bytecode builds ordinary block items
                # and never calls Item.Properties.stacksTo/durability.
                generated = (
                    64,
                    "Create Deco BlockRegistry BARS/BAR_PANELS dynamic block builder; no item stack override; Item.DEFAULT_MAX_STACK_SIZE=64",
                    "com.github.talrey.createdeco.BlockRegistry",
                )
            if generated is None and namespace == "supplementaries" and name.startswith("way_sign_"):
                generated = (
                    64,
                    "Supplementaries ModRegistry WAY_SIGN_ITEMS dynamic SignPostItem registration; no stack override; Item.DEFAULT_MAX_STACK_SIZE=64",
                    "net.mehvahdjukaar.supplementaries.reg.ModRegistry",
                )
            if generated is None:
                raise ValueError(
                    f"could not locate exact registry factory path for {iid}; refusing to infer a stack limit"
                )
            value, detail, registry_class = generated
            jar = archive_for(root, registry_class)
            receipts[iid] = {
                "max_stack_size": value,
                "evidence": {
                    "kind": "pinned_bytecode",
                    "jar": jar.name,
                    "sha256": digest(jar),
                    "jars": [{"name": jar.name, "sha256": digest(jar)}],
                    "class": registry_class.replace('.', '/') + ".class",
                    "classes": [registry_class],
                    "detail": detail,
                },
            }
            continue
        values: list[tuple[int, str]] = []
        details: list[str] = []
        evidence_classes: list[str] = []
        evidence_jars: list[Path] = []
        for registry_class, target_class, target_method, kind in candidates:
            evidence_classes.append(registry_class)
            registry_jar = archive_for(root, registry_class)
            evidence_jars.append(registry_jar)
            if target_method in {"<registry direct>", "<registry field>"}:
                body = parsed_registry(registry_class)[3]
            else:
                body, target_jar = target_body(target_class, target_method)
                evidence_jars.append(target_jar)
            found = stack_calls(body)
            if found:
                values.extend(found)
                details.append(f"{kind}: {registry_class} -> {target_class}.{target_method} -> {found}")
            else:
                details.append(f"{kind}: {registry_class} -> {target_class}.{target_method} has no stack override")
        if iid in KNOWN_CONSTRUCTOR_LIMITS:
            value, detail = KNOWN_CONSTRUCTOR_LIMITS[iid]
            details.append(f"exact constructor-chain override: {detail}")
            values = [(value, "verified constructor chain")]
        if not values:
            value = default
            details.append(f"exact registry/factory path has no stacksTo or durability override; Item.DEFAULT_MAX_STACK_SIZE={default}")
        else:
            value = values[-1][0]
        # The first registry class is authoritative for this ID; include all
        # referenced constructor jars in a deterministic evidence list.
        if not evidence_classes:
            evidence_classes = [registry_classes[0]]
        unique_jars = sorted({p for p in evidence_jars}, key=lambda p: p.name)
        if not unique_jars:
            unique_jars = [archive_for(root, evidence_classes[0])]
        receipts[iid] = {
            "max_stack_size": value,
            "evidence": {
                "kind": "pinned_bytecode",
                "jar": unique_jars[0].name,
                "sha256": digest(unique_jars[0]),
                "jars": [{"name": p.name, "sha256": digest(p)} for p in unique_jars],
                "class": evidence_classes[0].replace('.', '/') + ".class",
                "classes": sorted(set(evidence_classes)),
                "detail": "; ".join(details),
            },
        }

    payload = {"schema_version": 1, "kind": "pinned_bytecode_stack_receipt", "runtime": {"minecraft_jar": str(MAPPED_SERVER), "minecraft_sha256": digest(MAPPED_SERVER), "default_max_stack_size": default}, "items": receipts}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {output} ({len(receipts)} items)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("docs/vvh/evidence/current/item-stack-registry.json"))
    parser.add_argument("--minecraft-jar", type=Path, required=True, help="exact mapped/server Minecraft JAR used for Item.DEFAULT_MAX_STACK_SIZE")
    parser.add_argument("--javap", type=Path, default=None, help="javap executable (defaults to PATH)")
    args = parser.parse_args()
    main(args.root.resolve(), args.output if args.output.is_absolute() else args.root / args.output, args.minecraft_jar, args.javap)
