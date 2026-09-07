"""Focused regression tests for catalog provenance and stack validation."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import vvh_campaign_v3_validate as validator
import vvh_sync_catalog as catalog


class CatalogValidationTests(unittest.TestCase):
    def test_unknown_stack_size_is_not_coerced_to_64(self) -> None:
        self.assertIsNone(validator.stack_limit_for_item("example:future_item", {}))
        self.assertEqual(validator.stack_limit_for_item("minecraft:shield", {}), 1)

    def test_only_reviewed_receipt_supplies_stack_limits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "project.json").write_text(json.dumps({"items": {"example:guess": 64}}))
            self.assertEqual(catalog.load_stack_metadata(root)[0], {})
            path = root / "docs/vvh/evidence/current/item-stack-registry.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"kind": "pinned_bytecode_stack_receipt", "items": {
                "example:crate": {"max_stack_size": 16, "evidence": {
                    "kind": "pinned_bytecode", "sha256": "a" * 64, "class": "example/Items.class"}}
            }}))
            self.assertEqual(catalog.load_stack_metadata(root)[0], {"example:crate": 16})
            path.write_text(json.dumps({"items": {"example:guess": 64}}))
            with self.assertRaises(ValueError):
                catalog.load_stack_metadata(root)

    def test_current_crates_keep_real_payment_ids_and_shared_claims(self) -> None:
        import vvh_campaign_v3 as source
        market = {q["id"]: q for q in source.build_campaign()[0][4].quests}
        for quest_local, task_local in ((0x11, 0x21), (0x12, 0x22), (0x13, 0x23), (0x14, 0x24)):
            quest = market[source.qid(5, quest_local)]
            payment = next(t for t in quest["tasks"] if t["id"] == source.tid(5, task_local))
            self.assertTrue(payment["consume_items"])
            self.assertFalse(payment.get("task_screen_only", False))
            for reward in quest["rewards"]:
                self.assertTrue(reward["team_reward"])
                self.assertTrue(reward["exclude_from_claim_all"])
                self.assertEqual(reward["auto"], "disabled")

    def test_stack_bytecode_parser_keeps_nonstandard_limits(self) -> None:
        from vvh_extract_stack_receipt import stack_calls
        self.assertEqual(stack_calls("10: bipush 16\n12: invokevirtual #1 // Method Item$Properties.stacksTo:(I)"), [(16, "Item.Properties.stacksTo")])
        self.assertEqual(stack_calls("10: sipush 400\n12: invokevirtual #1 // Method Item$Properties.durability:(I)"), [(1, "Item.Properties.durability")])


if __name__ == "__main__":
    unittest.main()
