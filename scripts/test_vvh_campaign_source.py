"""Regression tests for current VvH source/drift safeguards."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from vvh_campaign_v3 import (
    _ledger_drift,
    _ledger_for,
    _read_ledger,
    _stage_outputs,
    _verify_baseline_fixture,
    build_campaign,
    normalized_manifest,
    output_matches,
    qid,
    render_chapter,
)
from vvh_ch1_ch3_baseline_fixture import (
    BASELINE_QUEST_SHA256,
    BASELINE_SPROCKET_WORDING_DESCRIPTION,
    BASELINE_SPROCKET_WORDING_REWARD_TITLE,
    BASELINE_ARCANE_SPROCKET_DESCRIPTION,
    ARCANE_SPROCKET_WORDING_QUEST_ID,
    ARCANE_SPROCKET_WORDING_REWARD_ID,
    RABBIT_STEW_ORIGINAL_REWARD_ID,
    RABBIT_STEW_SPLIT_QUEST_ID,
    SPROCKET_WORDING_QUEST_ID,
    SPROCKET_WORDING_REWARD_ID,
)
from vvh_validate import Parser, SNBTNumber


# This is a compact, checked-in preservation fixture sourced from the live
# Chapter 4 baseline.  Content may be redesigned in place, but these IDs,
# coordinates, dependencies, and optional flags are save/layout contracts.
HOUSE_NIGHT_STRUCTURE = {
    "7A11C0DF00400001": (0, -10, ("7A11C0DF00200002",), False),
    "7A11C0DF00400002": (0, -7, ("7A11C0DF00400001",), False),
    "7A11C0DF00400003": (0, -4, ("7A11C0DF00400002",), False),
    "7A11C0DF00400004": (10.5, 0, ("7A11C0DF00400011",), True),
    "7A11C0DF00400005": (7.5, 2, ("7A11C0DF00400011",), True),
    "7A11C0DF00400006": (4.5, 3.5, ("7A11C0DF00400010",), True),
    "7A11C0DF00400007": (-4.5, 3.5, ("7A11C0DF0040000F",), True),
    "7A11C0DF00400008": (-7.5, 2, ("7A11C0DF0040000E",), True),
    "7A11C0DF00400009": (-10.5, 0, ("7A11C0DF0040000E",), True),
    "7A11C0DF0040000C": (1.5, 4.5, ("7A11C0DF00400010",), True),
    "7A11C0DF0040000D": (-1.5, 4.5, ("7A11C0DF0040000F",), True),
    "7A11C0DF0040000E": (-6.5, -1, ("7A11C0DF00400003",), True),
    "7A11C0DF0040000F": (-2.5, 0.5, ("7A11C0DF00400003",), True),
    "7A11C0DF00400010": (2.5, 0.5, ("7A11C0DF00400003",), True),
    "7A11C0DF00400011": (6.5, -1, ("7A11C0DF00400003",), True),
}

CHAPTER_1_TO_3_IDS = {
    1: (1, 6, 3, 7, 5),
    2: (1, 2, 3, 4, 7),
    3: (1, 2, 3, 14, 15, 16, 17, 4, 5, 6, 12, 8, 13, 7, 9),
}

# Existing currency reward identities are save keys.  A redesign may change
# the amount or description, but it must not allocate a fresh claim key.
HOUSE_NIGHT_CURRENCY_REWARD_IDS = {
    "7A11C0DF00400001": ("7A11C2DF00400001",),
    "7A11C0DF00400002": ("7A11C2DF0040005B",),
    "7A11C0DF00400003": ("7A11C2DF0040005E",),
    "7A11C0DF00400004": ("7A11C2DF00400070",),
    "7A11C0DF00400005": ("7A11C2DF00400025",),
    "7A11C0DF00400006": ("7A11C2DF0040001A",),
    "7A11C0DF00400007": ("7A11C2DF00400031",),
    "7A11C0DF00400008": ("7A11C2DF00400035",),
    "7A11C0DF00400009": ("7A11C2DF00400069",),
    "7A11C0DF0040000C": ("7A11C2DF00400029",),
    "7A11C0DF0040000D": ("7A11C2DF0040002D",),
    "7A11C0DF0040000E": ("7A11C2DF00400061",),
    "7A11C0DF0040000F": ("7A11C2DF00400063",),
    "7A11C0DF00400010": ("7A11C2DF00400065",),
    "7A11C0DF00400011": ("7A11C2DF00400067",),
}


class CampaignSourceTests(unittest.TestCase):
    @staticmethod
    def _canonical(value):
        if isinstance(value, SNBTNumber):
            return {"__snbt_number__": value.value, "kind": value.kind, "suffix": value.suffix}
        if isinstance(value, dict):
            return {key: CampaignSourceTests._canonical(child) for key, child in value.items()}
        if isinstance(value, list):
            return [CampaignSourceTests._canonical(child) for child in value]
        return value

    @classmethod
    def _quest_digest(cls, quest):
        quest = copy.deepcopy(quest)
        if quest["id"] == RABBIT_STEW_SPLIT_QUEST_ID:
            total = 0
            retained = []
            original = None
            for reward in quest.get("rewards", []):
                item = reward.get("item", {})
                if item.get("id") != "minecraft:rabbit_stew":
                    retained.append(reward)
                    continue
                count = item.get("count", reward.get("count", 1))
                total += count.value if isinstance(count, SNBTNumber) else count
                if reward.get("id") == RABBIT_STEW_ORIGINAL_REWARD_ID:
                    # Keep the original reward identity and all of its
                    # metadata while collapsing the sixteen one-item entries
                    # back to the pre-edit stack for semantic comparison.
                    original = reward
                    original["item"] = dict(original.get("item", {}))
                    retained.append(original)
            if original is None:
                raise AssertionError("rabbit-stew split lost its original reward identity")
            original["item"]["count"] = SNBTNumber(total, "int", "")
            quest["rewards"] = retained
        if quest["id"] == SPROCKET_WORDING_QUEST_ID:
            # The current wording explicitly names the ordinary Sprocket
            # currency.  Restore only the reviewed baseline copy for the
            # all-other-fields semantic digest.
            quest["description"] = [BASELINE_SPROCKET_WORDING_DESCRIPTION]
            for reward in quest.get("rewards", []):
                if reward.get("id") == SPROCKET_WORDING_REWARD_ID:
                    reward["title"] = BASELINE_SPROCKET_WORDING_REWARD_TITLE
        if quest["id"] == ARCANE_SPROCKET_WORDING_QUEST_ID:
            quest["description"] = [BASELINE_ARCANE_SPROCKET_DESCRIPTION]
            for reward in quest.get("rewards", []):
                if reward.get("id") == ARCANE_SPROCKET_WORDING_REWARD_ID:
                    reward["title"] = BASELINE_SPROCKET_WORDING_REWARD_TITLE
        raw = json.dumps(cls._canonical(quest), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def test_lossless_parser_distinguishes_loader_numeric_types(self) -> None:
        integer = Parser("{ value: 1 }", "test", preserve_numeric_types=True).parse()
        long_value = Parser("{ value: 1L }", "test", preserve_numeric_types=True).parse()
        plain_float = Parser("{ value: 1.0 }", "test", preserve_numeric_types=True).parse()
        double_value = Parser("{ value: 1.0d }", "test", preserve_numeric_types=True).parse()

        self.assertNotEqual(integer, long_value)
        self.assertNotEqual(plain_float, double_value)

    def test_source_drift_rejects_numeric_suffix_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.snbt"
            path.write_text("{ value: 1L }\n", encoding="utf-8")
            self.assertFalse(output_matches(path, "{ value: 1 }\n"))
            self.assertTrue(output_matches(path, "{ value: 1L }\n"))

    def test_hash_ledger_rejects_semantically_equal_external_edit(self) -> None:
        import hashlib

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "config" / "sample.snbt"
            path.parent.mkdir(parents=True)
            path.write_text("{ value: 1 }\n", encoding="utf-8")
            ledger = {
                "version": 1,
                "algorithm": "sha256",
                "managed_outputs": {
                    "config/sample.snbt": hashlib.sha256(path.read_bytes()).hexdigest(),
                },
            }
            path.write_text("{ value: 1 }\n\n", encoding="utf-8")
            drift = _ledger_drift(root, {path: "{ value: 1 }\n"}, ledger)
            self.assertTrue(any("external edit detected" in message for message in drift))

    def test_missing_and_corrupt_ledger_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertIsNone(_read_ledger(root))
            path = root / "docs" / "vvh" / "generated_output_hashes.json"
            path.parent.mkdir(parents=True)
            path.write_text("{ broken", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                _read_ledger(root)

    def test_generation_keeps_immutable_bootstrap_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "config" / "sample.snbt"
            path.parent.mkdir(parents=True)
            path.write_text("{ value: 1 }\n", encoding="utf-8")
            ledger_path = root / "docs" / "vvh" / "generated_output_hashes.json"
            ledger_path.parent.mkdir(parents=True)
            ledger_path.write_text(
                json.dumps({
                    "version": 1,
                    "algorithm": "sha256",
                    "managed_outputs": {"config/sample.snbt": "old"},
                    "bootstrap_receipt": {
                        "mode": "immutable-pre-edit-snapshot",
                        "fixture_hashes_sha256": {"config/sample.snbt": "fixture"},
                    },
                }),
                encoding="utf-8",
            )
            refreshed = _ledger_for(root, {path: "{ value: 1 }\n"})
            self.assertEqual(
                refreshed["bootstrap_receipt"]["fixture_hashes_sha256"]["config/sample.snbt"],
                "fixture",
            )

    def test_malformed_staged_candidate_does_not_touch_live_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            live = root / "config" / "ftbquests" / "quests" / "chapters" / "ch01_island_charter.snbt"
            live.parent.mkdir(parents=True)
            live.write_text("{ original: true }\n", encoding="utf-8")
            expected = {live: "{ malformed: [ }\n"}
            with self.assertRaises(Exception):
                _stage_outputs(root, expected)
            self.assertEqual(live.read_text(encoding="utf-8"), "{ original: true }\n")

    def test_initial_baseline_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            baseline = Path(directory) / "baseline"
            live = root / "config" / "ftbquests" / "quests" / "chapters" / "ch01_island_charter.snbt"
            fixture = baseline / "quests" / "chapters" / "ch01_island_charter.snbt"
            live.parent.mkdir(parents=True)
            fixture.parent.mkdir(parents=True)
            live.write_text("{ value: 2 }\n", encoding="utf-8")
            fixture.write_text("{ value: 1 }\n", encoding="utf-8")
            errors, _ = _verify_baseline_fixture(root, {live: fixture.read_text()}, baseline)
            self.assertTrue(any("bytes differ" in message for message in errors))
            self.assertEqual(live.read_text(encoding="utf-8"), "{ value: 2 }\n")

    def test_house_night_structure_is_save_and_layout_stable(self) -> None:
        chapters, _ = build_campaign()
        house = next(chapter for chapter in chapters if chapter.number == 4)
        actual = {
            quest["id"]: (
                quest["x"],
                quest["y"],
                tuple(quest.get("dependencies", [])),
                quest.get("optional", False),
            )
            for quest in house.quests
        }
        self.assertEqual(actual, HOUSE_NIGHT_STRUCTURE)

    def test_first_thirst_semantics_and_reward_ids_are_preserved(self) -> None:
        chapters, _ = build_campaign()
        house = next(chapter for chapter in chapters if chapter.number == 4)
        first = next(quest for quest in house.quests if quest["id"] == "7A11C0DF00400001")
        self.assertEqual(first["shape"], "hexagon")
        self.assertEqual(first["size"], 1.4)
        self.assertEqual(first["icon"], {"id": "vampirism:altar_inspiration"})
        self.assertEqual([task["id"] for task in first["tasks"]], [
            "7A11C1DF00400001", "7A11C1DF00400002", "7A11C1DF00400003",
        ])
        self.assertEqual([reward["id"] for reward in first["rewards"]], [
            "7A11C2DF00400001", "7A11C2DF00400002", "7A11C2DF00400003",
            "7A11C2DF00400004",
        ])
        self.assertEqual(first["rewards"][0]["item"]["id"], "numismatics:bevel")
        self.assertEqual(first["rewards"][1]["item"]["id"], "vampirism:vampire_cloak_red_black")

    def test_effective_dependency_visibility_is_chapter_scoped(self) -> None:
        chapters, groups = build_campaign()
        manifest = normalized_manifest(chapters, groups)
        for chapter in manifest["chapters"]:
            expected = chapter["filename"] == "ch05_market_services"
            self.assertTrue(all(q["hide_dependency_lines"] is expected for q in chapter["quests"]))

    def test_chapters_one_to_three_keep_the_reconciled_quest_id_fixture(self) -> None:
        chapters, _ = build_campaign()
        for chapter_number, indexes in CHAPTER_1_TO_3_IDS.items():
            chapter = next(chapter for chapter in chapters if chapter.number == chapter_number)
            self.assertEqual(
                [quest["id"] for quest in chapter.quests],
                [qid(chapter_number, index) for index in indexes],
            )

    def test_chapters_one_to_three_match_full_live_semantic_fixture(self) -> None:
        chapters, _ = build_campaign()
        actual = {}
        for chapter in chapters[:3]:
            parsed = Parser(render_chapter(chapter), chapter.filename, preserve_numeric_types=True).parse()
            actual.update({quest["id"]: self._quest_digest(quest) for quest in parsed["quests"]})
        self.assertEqual(set(actual), set(BASELINE_QUEST_SHA256))
        self.assertEqual(actual, BASELINE_QUEST_SHA256)
        ch3 = next(chapter for chapter in chapters if chapter.number == 3)
        ch3_quest = next(quest for quest in ch3.quests if quest["id"] == RABBIT_STEW_SPLIT_QUEST_ID)
        self.assertIn(
            RABBIT_STEW_ORIGINAL_REWARD_ID,
            [reward["id"] for reward in ch3_quest.get("rewards", [])],
        )

    def test_ch3_sprocket_reward_names_ordinary_currency(self) -> None:
        chapters, _ = build_campaign()
        ch3 = next(chapter for chapter in chapters if chapter.number == 3)
        quest = next(quest for quest in ch3.quests if quest["id"] == SPROCKET_WORDING_QUEST_ID)
        reward = next(reward for reward in quest["rewards"] if reward["id"] == SPROCKET_WORDING_REWARD_ID)
        self.assertEqual(reward["title"], "1 Sprocket")
        description = " ".join(quest["description"])
        self.assertIn("one Sprocket to spend at the Market", description)
        self.assertNotIn("construction grant", description.lower())

    def test_ch3_arcane_sprocket_reward_names_ordinary_currency(self) -> None:
        chapters, _ = build_campaign()
        ch3 = next(chapter for chapter in chapters if chapter.number == 3)
        quest = next(quest for quest in ch3.quests if quest["id"] == ARCANE_SPROCKET_WORDING_QUEST_ID)
        reward = next(reward for reward in quest["rewards"] if reward["id"] == ARCANE_SPROCKET_WORDING_REWARD_ID)
        self.assertEqual(reward["title"], "1 Sprocket")
        description = " ".join(quest["description"])
        self.assertIn("one Sprocket to spend on the Celestial Spire Crate", description)
        self.assertNotIn("construction grant", description.lower())

    def test_house_night_currency_reward_keys_remain_stable(self) -> None:
        chapters, _ = build_campaign()
        house = next(chapter for chapter in chapters if chapter.number == 4)
        for quest in house.quests:
            expected = HOUSE_NIGHT_CURRENCY_REWARD_IDS[quest["id"]]
            actual = tuple(
                reward["id"]
                for reward in quest.get("rewards", [])
                if reward.get("item", {}).get("id", "").startswith("numismatics:")
            )
            self.assertEqual(actual, expected, quest["id"])


if __name__ == "__main__":
    unittest.main()
