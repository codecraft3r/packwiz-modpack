"""Regression coverage for the progression-aware campaign integration."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import frontier_campaign as frontier
import frontier_validate
import vvh_campaign_v3 as source
from vvh_validate import Parser

ROOT = Path(__file__).resolve().parents[1]

class FrontierCampaignTests(unittest.TestCase):
    def fixture(self):
        temp = tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        shutil.copytree(ROOT / 'docs/frontier', root / 'docs/frontier')
        proofs = json.loads((root / 'docs/frontier/evidence/pack-provenance.json').read_text())
        for proof in proofs.values():
            target = root / proof['metadata'];target.parent.mkdir(exist_ok=True)
            shutil.copy2(ROOT / proof['metadata'], target)
        for path, text in source.outputs(root).items():
            path.parent.mkdir(parents=True, exist_ok=True);path.write_text(text)
        return root

    def test_combined_book_preserves_every_archived_quest(self):
        report = frontier_validate.audit(self.fixture())
        self.assertEqual(report['errors'], [])
        self.assertEqual((report['new_quests'], report['archived_quests'], report['total_quests']), (81, 59, 140))

    def test_external_reward_edit_is_rejected(self):
        root = self.fixture();path = root / 'config/ftbquests/quests/chapters/frontier_02_bosses.snbt'
        data = Parser(path.read_text(), str(path)).parse();data['quests'][0]['rewards'][0]['count'] = 64
        path.write_text(source.snbt(data))
        self.assertTrue(any('differs from source' in e for e in frontier_validate.audit(root)['errors']))

    def test_changed_mod_pin_invalidates_artifact_proof(self):
        root = self.fixture();proof = json.loads((root / 'docs/frontier/evidence/pack-provenance.json').read_text())['cataclysm']
        path = root / proof['metadata'];path.write_text(path.read_text()+'\n# new pin requires fresh evidence\n')
        self.assertTrue(any('stale pinned-artifact proof' in e for e in frontier_validate.audit(root)['errors']))

    def test_weak_checks_do_not_issue_currency_and_purchases_are_shared(self):
        manifest = frontier.load(ROOT)
        for q in manifest['quests']:
            if all(t['type'] == 'checkmark' for t in q['tasks']):
                self.assertEqual(frontier_validate.currency(q['rewards']), 0, q['key'])
                self.assertFalse(q['repeat'], q['key'])
            if q['kind'] == 'shop':
                self.assertGreater(frontier_validate.currency(q['tasks']), 0)
                self.assertTrue(all(t['consume_items'] and t['task_screen_only'] for t in q['tasks']))
                self.assertTrue(all(r['team_reward'] for r in q['rewards']))

    def test_choice_table_long_survives_archive_composition(self):
        root = self.fixture()
        path = root / 'config/ftbquests/quests/chapters/ch03_lantern_order.snbt'
        self.assertRegex(path.read_text(), r'table_id: \d+L')

    def test_existing_advancements_are_ungated_and_whole(self):
        root = self.fixture()
        for path, content in source.outputs(root).items():
            if path.stem not in frontier.chapter_names(root):continue
            for q in Parser(content,str(path)).parse()['quests']:
                if all(t['type'] == 'advancement' for t in q['tasks']):
                    self.assertFalse(q.get('dependencies'))
                    self.assertEqual(q['progression_mode'],'flexible')
                    self.assertTrue(all(t['criterion']=='' for t in q['tasks']))

if __name__ == '__main__':unittest.main()
