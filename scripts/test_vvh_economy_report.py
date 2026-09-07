"""Deterministic fixtures for the VvH source-level economy report."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = Path(__file__).with_name("vvh_economy_report.py")
spec = importlib.util.spec_from_file_location("vvh_economy_report_fixture", REPORT_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import {REPORT_PATH}")
report_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = report_module
spec.loader.exec_module(report_module)


class EconomyReportFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = report_module.build_report(ROOT, fragmented_teams=2, team_members=2, fixed_population=2)

    def test_fixed_population_formula(self) -> None:
        one_time = self.report["one_time"]
        fixed = self.report["affordability"]["fixed_population"]
        one_team = fixed["single_team"]
        solo = fixed["solo_teams"]
        self.assertEqual(one_team["total_pool_bevel_equivalent"], one_time["personal_bevel_equivalent"] * 2 + one_time["team_bevel_equivalent"])
        self.assertEqual(solo["aggregate_total_pool_bevel_equivalent"], one_time["personal_bevel_equivalent"] * 2 + one_time["team_bevel_equivalent"] * 2)
        self.assertEqual(one_team["weekly_faucet_bevel_equivalent"], self.report["repeatable"]["weekly_faucet_reward_bevel_equivalent_per_team"])
        self.assertEqual(solo["aggregate_weekly_faucet_bevel_equivalent"], one_team["weekly_faucet_bevel_equivalent"] * 2)

    def test_currency_accounting_and_board_price(self) -> None:
        basis = self.report["currency_basis_bevel"]
        self.assertEqual(basis["numismatics:bevel"], 1.0)
        self.assertEqual(basis["numismatics:sprocket"], 2.0)
        self.assertEqual(basis["numismatics:cog"], 8.0)
        paid = self.report["repeatable"]["services"]
        computed = sum(row["price_bevel"] for row in paid if row["kind"] == "paid_sink")
        self.assertEqual(computed, self.report["affordability"]["paid_board_cost_bevel_equivalent"])
        self.assertGreater(computed, 0)


if __name__ == "__main__":
    unittest.main()
