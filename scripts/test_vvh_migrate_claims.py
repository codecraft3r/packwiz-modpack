#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from vvh_migrate_claims import Parser, dump, transform


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.source = """{
            version: 1
            uuid: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            name: "Fixture team"
            lock: false
            rewards_blocked: false
            task_progress: { "T1": 2L }
            started: { "Q1": 100L }
            completed: { "Q1": 200L }
            repeatable: { "Q1": 500L }
            completion_count: { "Q1": 3 }
            claimed_rewards: {
                "11111111111111111111111111111111:R1": 900L
                "22222222222222222222222222222222:R1": 700L
                "00000000000000000000000000000000:R2": 800L
            }
            player_data: {
                "11111111111111111111111111111111": { pinned_quests: [ "Q1" ] }
            }
        }"""
        self.spec = {
            "quest_ids": {"Q1": "Q9"},
            "task_ids": {"T1": "T9"},
            "reward_ids": {"R2": "R3"},
            "scope_transitions": [
                {"old_reward_id": "R1", "from": "personal", "to": "shared"}
            ],
        }

    def test_claim_scope_transition_consolidates_without_regrant(self):
        result = transform(Parser(self.source).parse(), self.spec)
        claims = result["claimed_rewards"]
        self.assertEqual(claims["00000000000000000000000000000000:R1"].raw, "700L")
        self.assertEqual(claims["00000000000000000000000000000000:R3"].raw, "800L")
        self.assertNotIn("11111111111111111111111111111111:R1", claims)
        self.assertEqual(result["started"]["Q9"].raw, "100L")
        self.assertEqual(result["repeatable"]["Q9"].raw, "500L")
        self.assertEqual(result["task_progress"]["T9"].raw, "2L")
        self.assertEqual(result["player_data"]["11111111111111111111111111111111"]["pinned_quests"], ["Q9"])

    def test_round_trip_preserves_uuid_key_shape_and_parses(self):
        result = transform(Parser(self.source).parse(), self.spec)
        encoded = dump(result) + "\n"
        reparsed = Parser(encoded).parse()
        self.assertIn('"00000000000000000000000000000000:R1"', encoded)
        self.assertEqual(reparsed["claimed_rewards"].keys(), result["claimed_rewards"].keys())

    def test_shared_to_personal_is_rejected_without_player_mapping(self):
        spec = {
            "scope_transitions": [
                {"old_reward_id": "R2", "from": "shared", "to": "personal"}
            ]
        }
        with self.assertRaises(ValueError):
            transform(Parser(self.source).parse(), spec)

    def test_claim_fanout_marks_every_new_entitlement_claimed(self):
        spec = {
            "reward_claim_copies": {
                "R1": ["R1", "R1A", "R1B"]
            }
        }
        result = transform(Parser(self.source).parse(), spec)
        claims = result["claimed_rewards"]
        self.assertEqual(
            {key for key in claims if key.startswith("11111111111111111111111111111111:")},
            {
                "11111111111111111111111111111111:R1",
                "11111111111111111111111111111111:R1A",
                "11111111111111111111111111111111:R1B",
            },
        )
        self.assertEqual(claims["11111111111111111111111111111111:R1A"].raw, "900L")

    def test_duplicate_snbt_keys_are_rejected(self):
        with self.assertRaises(ValueError):
            Parser('{a: 1 a: 2}').parse()

    def test_corrupt_snbt_apply_does_not_create_backup_or_mutate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "team.snbt"
            mapping = root / "mapping.json"
            source.write_text('{claimed_rewards: {"bad": 1L}', encoding="utf-8")
            original = source.read_text(encoding="utf-8")
            mapping.write_text(json.dumps({"scope_transitions": []}), encoding="utf-8")
            expected = hashlib.sha256(source.read_bytes()).hexdigest()
            cmd = [sys.executable, str(Path(__file__).parent / "vvh_migrate_claims.py"), str(source), "--mapping", str(mapping), "--apply", "--expected-sha256", expected]
            failed = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertFalse((root / "team.snbt.bak").exists())

    def test_reviewed_mapping_fixture_has_required_transitions_and_fanout(self):
        mapping_path = Path(__file__).parents[1] / "docs/vvh/evidence/save-migration-mapping.json"
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        transitions = {item["old_reward_id"] for item in mapping["scope_transitions"]}
        self.assertTrue({
            "7A11C2DF00400061",
            "7A11C2DF00400063",
            "7A11C2DF00400065",
            "7A11C2DF00400067",
        } <= transitions)
        self.assertEqual(
            mapping["reward_claim_copies"]["7A11C2DF0030005E"][1:],
            [f"7A11C2DF003050{i:02X}" for i in range(1, 16)],
        )
        self.assertEqual(
            mapping["reward_claim_copies"]["7A11C2DF00500018"],
            ["7A11C2DF00500018", "7A11C2DF005050A0"],
        )
        self.assertEqual(
            mapping["reward_claim_copies"]["7A11C2DF0050001B"],
            [f"7A11C2DF005050A{i:X}" for i in range(1, 5)],
        )
        self.assertEqual(
            mapping["reward_claim_copies"]["7A11C2DF00500042"],
            ["7A11C2DF00500042", "7A11C2DF0050A0D4"],
        )
        self.assertEqual(
            mapping["reward_claim_copies"]["7A11C2DF00400036"],
            ["7A11C2DF00400036"] + [f"7A11C2DF0040510{i:X}" for i in range(7)],
        )

    def test_reviewed_mapping_matches_current_generator_scope_transitions_and_splits(self):
        import vvh_campaign_v3

        mapping_path = Path(__file__).parents[1] / "docs/vvh/evidence/save-migration-mapping.json"
        baseline_path = Path(__file__).parents[1] / "docs/vvh/evidence/save-migration-baseline.json"
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        expected_outputs = vvh_campaign_v3.outputs(Path(__file__).parents[1])
        mapped = {item["old_reward_id"] for item in mapping["scope_transitions"]}
        actual = set()
        current_by_quest = {}
        for path, text in expected_outputs.items():
            if path.name in {"ch03_lantern_order.snbt", "ch04_house_night.snbt", "ch05_market_services.snbt"}:
                current = Parser(text).parse()
                current_by_quest.update({quest["id"]: quest for quest in current["quests"]})
        for group in baseline["scope_transitions"]:
            self.assertFalse(group["team_reward"])
            quest = current_by_quest[group["quest_id"]]
            rewards = {reward["id"]: reward for reward in quest.get("rewards", [])}
            for reward_id in group["reward_ids"]:
                self.assertIn(reward_id, rewards)
                current_reward = rewards[reward_id]
                self.assertTrue(current_reward["team_reward"])
                self.assertEqual(current_reward["item"]["id"], group["item"])
                self.assertGreater(group["count"], 0)
                actual.add(reward_id)
        actual_copies = {split["reward_id"]: split["targets"] for split in baseline["claim_splits"]}
        for split in baseline["claim_splits"]:
            quest = current_by_quest[split["quest_id"]]
            rewards = {reward["id"]: reward for reward in quest.get("rewards", [])}
            for target in split["targets"]:
                self.assertIn(target, rewards)
                self.assertEqual(rewards[target]["item"]["id"], split["item"])
                self.assertEqual(int(rewards[target]["item"]["count"].raw.rstrip("bBsSlLfFdD")), 1)
        self.assertEqual(mapped, actual)
        self.assertEqual(mapping["reward_claim_copies"], actual_copies)

    def test_reviewed_mapping_transforms_realistic_claims(self):
        mapping_path = Path(__file__).parents[1] / "docs/vvh/evidence/save-migration-mapping.json"
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        source = """{
            version: 1L
            claimed_rewards: {
                "11111111111111111111111111111111:7A11C2DF0030005E": 100L
                "11111111111111111111111111111111:7A11C2DF00400065": 200L
                "22222222222222222222222222222222:7A11C2DF00500001": 300L
            }
            completion_count: { "7A11C0DF00400010": 2 }
        }"""
        result = transform(Parser(source).parse(), mapping)
        claims = result["claimed_rewards"]
        for index in range(0x5001, 0x5010):
            self.assertIn(f"11111111111111111111111111111111:7A11C2DF0030{index:04X}", claims)
        self.assertIn("00000000000000000000000000000000:7A11C2DF00400065", claims)
        self.assertIn("00000000000000000000000000000000:7A11C2DF00500001", claims)

    def test_apply_requires_hash_and_creates_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "team.snbt"
            mapping = root / "mapping.json"
            source.write_text(self.source, encoding="utf-8")
            mapping.write_text(json.dumps(self.spec), encoding="utf-8")
            wrong = "0" * 64
            cmd = [sys.executable, str(Path(__file__).parent / "vvh_migrate_claims.py"), str(source), "--mapping", str(mapping), "--apply", "--expected-sha256", wrong]
            failed = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(source.read_text(encoding="utf-8"), self.source)
            expected = hashlib.sha256(source.read_bytes()).hexdigest()
            ok = subprocess.run(cmd[:-1] + [expected], capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertTrue((root / "team.snbt.bak").exists())
            self.assertNotEqual(source.read_text(encoding="utf-8"), self.source)


if __name__ == "__main__":
    unittest.main()
