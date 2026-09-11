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
        overrides = json.loads((root / 'docs/frontier/evidence/survival-paths.json').read_text())['pack_overrides']
        for relative in overrides:
            target = root / relative;target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        proofs = json.loads((root / 'docs/frontier/evidence/pack-provenance.json').read_text())
        for proof in proofs.values():
            target = root / proof['metadata'];target.parent.mkdir(exist_ok=True)
            shutil.copy2(ROOT / proof['metadata'], target)
        graph_runtime = json.loads((root / 'docs/frontier/evidence/graph-runtime.json').read_text())
        target = root / graph_runtime['metadata'];target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / graph_runtime['metadata'], target)
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

    def test_existing_advancements_are_connected_flexible_and_whole(self):
        root = self.fixture()
        manifest = frontier.load(root)
        for source_q in manifest['quests']:
            if not all(t['type'] == 'advancement' for t in source_q['tasks']):
                continue
            chapter = root / 'config/ftbquests/quests/chapters' / ('frontier_' + source_q['chapter'] + '.snbt')
            emitted = next(q for q in Parser(chapter.read_text(), str(chapter)).parse()['quests']
                           if q['id'] == frontier.ident('quest:' + source_q['key']))
            if source_q['key'] != 'welcome':
                self.assertTrue(source_q['deps'], source_q['key'])
                self.assertTrue(emitted.get('dependencies'), source_q['key'])
            self.assertEqual(emitted['progression_mode'], 'flexible', source_q['key'])
            self.assertTrue(all(t['criterion'] == '' for t in emitted['tasks']))

    def change_quest(self, root, key, change):
        path = root / frontier.SOURCE_REL
        manifest = json.loads(path.read_text())
        change(next(q for q in manifest['quests'] if q['key'] == key))
        path.write_text(json.dumps(manifest))
        for path, content in source.outputs(root).items():
            path.write_text(content)

    def test_bulk_rewards_use_actual_limits_not_a_blanket_64(self):
        for key, item, count in [('first_photo', 'exposure:color_film', 17),
                                 ('cinema', 'vista:hollow_cassette', 2)]:
            with self.subTest(item=item):
                root = self.fixture()
                def change(q):
                    next(r for r in q['rewards'] if r['item']['id'] == item)['count'] = count
                self.change_quest(root, key, change)
                self.assertTrue(any('exceeds verified stack limit' in e for e in frontier_validate.audit(root)['errors']))

    def test_missing_bulk_receipt_fails_closed(self):
        root = self.fixture();path = root / 'docs/frontier/evidence/reward-stack-limits.json'
        receipt = json.loads(path.read_text());del receipt['items']['exposure:color_film']
        path.write_text(json.dumps(receipt))
        self.assertTrue(any('exceeds verified stack limit' in e for e in frontier_validate.audit(root)['errors']))

    def test_missing_survival_path_fails_closed(self):
        root = self.fixture();path = root / 'docs/frontier/evidence/survival-paths.json'
        receipt = json.loads(path.read_text());del receipt['items']['vista:hollow_cassette']
        path.write_text(json.dumps(receipt))
        self.assertTrue(any('missing survival obtainability' in e for e in frontier_validate.audit(root)['errors']))

    def test_recipe_override_changes_invalidate_the_receipt(self):
        root = self.fixture();path = root / 'kubejs/server_scripts/crafting.js'
        path.write_text(path.read_text()+'\n// changed recipe needs renewed evidence\n')
        self.assertTrue(any('survival recipe evidence is stale' in e for e in frontier_validate.audit(root)['errors']))

    def test_purchases_cannot_become_free_inventory_checks(self):
        root = self.fixture()
        self.change_quest(root, 'shop_mending', lambda q: q['tasks'][0].update(consume_items=False))
        self.assertTrue(any('positive manual coin payment' in e for e in frontier_validate.audit(root)['errors']))

    def test_price_copy_must_match_payment(self):
        root = self.fixture()
        self.change_quest(root, 'shop_mending', lambda q: q['description'].__setitem__(1, 'Price: 16 Spurs.'))
        self.assertTrue(any('advertised price differs' in e for e in frontier_validate.audit(root)['errors']))

    def test_repeat_income_requires_progress_and_fresh_work(self):
        for change, message in [(lambda q: q.update(deps=[]), 'one-time progression gate'),
                                (lambda q: q['tasks'][0].update(consume_items=False), 'fresh work or consumed inputs')]:
            with self.subTest(message=message):
                root = self.fixture();self.change_quest(root, 'galley_contract', change)
                self.assertTrue(any(message in e for e in frontier_validate.audit(root)['errors']))

    def test_milestones_cannot_become_repeatable_faucets(self):
        root = self.fixture();self.change_quest(root, 'brass', lambda q: q.update(repeat=60))
        self.assertTrue(any('one-time reward made repeatable' in e for e in frontier_validate.audit(root)['errors']))

    def test_enchanted_book_cannot_gain_illegal_levels(self):
        root = self.fixture()
        def change(q):
            q['rewards'][0]['item']['components']['minecraft:stored_enchantments']['levels']['minecraft:mending'] = 10
        self.change_quest(root, 'shop_mending', change)
        self.assertTrue(any('invalid enchanted-book component' in e for e in frontier_validate.audit(root)['errors']))

    def test_external_prerequisite_requires_one_local_link(self):
        root = self.fixture()
        path = root / frontier.SOURCE_REL
        manifest = json.loads(path.read_text())
        chapter = next(c for c in manifest['chapters'] if c['key'] == '05_transport')
        quest = next(q for q in manifest['quests'] if q['key'] == 'flight_test')
        quest['deps'] = ['first_photo']
        chapter['links'] = [link for link in chapter.get('links', []) if link.get('quest') != 'first_photo']
        path.write_text(json.dumps(manifest))
        for output, content in source.outputs(root).items():
            output.parent.mkdir(parents=True, exist_ok=True);output.write_text(content)
        self.assertTrue(any('needs exactly one local' in e for e in frontier_validate.audit(root)['errors']))

    def test_disconnected_milestone_is_rejected(self):
        root = self.fixture()
        self.change_quest(root, 'shop_legendary', lambda q: q.update(deps=[]))
        self.assertTrue(any('disconnected from welcome' in e for e in frontier_validate.audit(root)['errors']))

    def test_crew_confirmed_cannot_be_flexible(self):
        root = self.fixture()
        path = root / 'config/ftbquests/quests/chapters/frontier_05_transport.snbt'
        data = Parser(path.read_text(), str(path)).parse()
        quest = next(q for q in data['quests'] if q['id'] == frontier.ident('quest:flight_test'))
        quest['progression_mode'] = 'flexible'
        path.write_text(source.snbt(data))
        self.assertTrue(any('progression mode does not match quest kind' in e for e in frontier_validate.audit(root)['errors']))

    def test_source_shape_must_be_verified_by_shipped_runtime(self):
        root = self.fixture()
        self.change_quest(root, 'brass', lambda q: q.update(shape='star'))
        self.assertTrue(any('unsupported shipped quest shape' in e for e in frontier_validate.audit(root)['errors']))

    def test_emitted_layout_cannot_drift_from_authored_source(self):
        root = self.fixture()
        path = root / 'config/ftbquests/quests/chapters/frontier_04_engineering.snbt'
        data = Parser(path.read_text(), str(path)).parse()
        quest = next(q for q in data['quests'] if q['id'] == frontier.ident('quest:brass'))
        quest['x'] += 1
        path.write_text(source.snbt(data))
        self.assertTrue(any('emitted x differs from source' in e or 'emitted file differs from source' in e
                            for e in frontier_validate.audit(root)['errors']))

    def test_faction_branches_cannot_cross_lock(self):
        root = self.fixture()
        self.change_quest(root, 'hunter_master', lambda q: q.update(deps=['vampire_master']))
        self.assertTrue(any('faction cross-lock' in e for e in frontier_validate.audit(root)['errors']))

if __name__ == '__main__':unittest.main()
