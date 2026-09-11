"""Focused regression checks for the source-level layout renderer."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import vvh_render_layouts as renderer


class RendererTests(unittest.TestCase):
    def test_cross_chapter_link_is_a_visual_endpoint_for_local_dependency(self):
        target_id = "AAAAAAAAAAAAAAAA"
        link_id = "1111111111111111"
        manifest = {"chapters": [
            {"filename": "origin", "quests": [{"id": target_id, "title": "Origin quest", "icon": {"id": "minecraft:compass"},
                                                   "x": 0, "y": 0, "dependencies": ["BBBBBBBBBBBBBBBB"]}]},
            {"filename": "destination", "quests": [{"id": "CCCCCCCCCCCCCCCC", "title": "Follow up", "x": 4, "y": 0,
                                                        "dependencies": [target_id]}],
             "quest_links": [{"id": link_id, "linked_quest": target_id, "x": 1.5, "y": 2.0, "shape": "diamond", "size": 0.8}]},
        ]}
        normalized = renderer.normalize_manifest(manifest)
        destination = normalized["chapters"][1]
        visuals = renderer.render_quests(destination)
        follow_up = next(q for q in visuals if q["id"] == "CCCCCCCCCCCCCCCC")
        linked = next(q for q in visuals if q["id"] == link_id)
        self.assertEqual(follow_up["dependencies"], [link_id])
        self.assertTrue(linked["is_quest_link"])
        self.assertEqual(linked["linked_quest"], target_id)
        self.assertEqual(linked["title"], "Origin quest")
        self.assertEqual(linked["icon"], "minecraft:compass")
        # The omitted ancestor is outside the destination chapter and should
        # not turn into a phantom missing dependency.
        metrics = renderer.graph_metrics(destination)
        self.assertEqual(metrics["missing_dependency_nodes"], 0)
        self.assertEqual(metrics["linked_visual_nodes"], 1)

    def test_link_shape_and_size_are_rendered_without_copying_rewards(self):
        manifest = {"chapters": [{"filename": "shapes", "quests": [{"id": "AAAAAAAAAAAAAAAA", "title": "Target",
                                                                          "x": 0, "y": 0, "shape": "circle",
                                                                          "rewards": [{"id": "reward"}]}],
                                   "quest_links": [{"id": "2222222222222222", "linked_quest": "AAAAAAAAAAAAAAAA",
                                                     "x": 3.25, "y": -1.5, "shape": "hexagon", "size": 1.3}]}]}
        chapter = renderer.normalize_manifest(manifest)["chapters"][0]
        link = next(q for q in renderer.render_quests(chapter) if q.get("is_quest_link"))
        self.assertEqual((link["x"], link["y"], link["shape"], link["size"]), (3.25, -1.5, "hexagon", 1.3))
        self.assertNotIn("rewards", link)
        self.assertIsNotNone(renderer.shape_points(link["shape"], (0, 0), 20 * link["size"]))
        with tempfile.TemporaryDirectory() as tmp:
            output, metrics = renderer.render_chapter(chapter, {}, {}, set(), set(), Path(tmp), 0, detail=True)
            self.assertTrue(output.exists())
            self.assertEqual(metrics["linked_visual_nodes"], 1)

    def test_bad_link_target_is_retained_and_reported(self):
        manifest = {"chapters": [{"filename": "broken", "quests": [{"id": "AAAAAAAAAAAAAAAA", "title": "Only quest"}],
                                   "quest_links": [{"id": "3333333333333333", "linked_quest": "DOES_NOT_EXIST",
                                                     "x": 0, "y": 0, "shape": "diamond", "size": 0.8}]}]}
        chapter = renderer.normalize_manifest(manifest)["chapters"][0]
        self.assertEqual(len(chapter["quest_links"]), 1)
        self.assertEqual(len([q for q in renderer.render_quests(chapter) if q.get("is_quest_link")]), 0)
        self.assertTrue(any("DOES_NOT_EXIST" in message and "missing" in message for message in chapter["quest_link_errors"]))
        self.assertEqual(renderer.graph_metrics(chapter)["missing_dependency_nodes"], 0)

    def test_chapters_from_root_resolves_native_snbt_links_across_files(self):
        target = "AAAAAAAAAAAAAAAA"
        link = "5555555555555555"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "quests"
            (root / "chapters").mkdir(parents=True)
            (root / "chapters" / "01_origin.snbt").write_text(
                '{ title: "Origin" quests: [{ id: AAAAAAAAAAAAAAAA title: "Target" x: 0 y: 0 }] }', encoding="utf-8")
            (root / "chapters" / "02_destination.snbt").write_text(
                '{ title: "Destination" quest_links: [{ id: 5555555555555555 linked_quest: AAAAAAAAAAAAAAAA x: 2 y: 1 shape: diamond size: 0.8 }] quests: [{ id: CCCCCCCCCCCCCCCC title: "Next" x: 4 y: 0 dependencies: [AAAAAAAAAAAAAAAA] }] }', encoding="utf-8")
            loaded = renderer.chapters_from_root(root)
        destination = loaded["chapters"][1]
        self.assertEqual(destination["quest_links"][0]["id"], link)
        next_node = next(q for q in renderer.render_quests(destination) if q["id"] == "CCCCCCCCCCCCCCCC")
        self.assertEqual(next_node["dependencies"], [link])

    def test_normalization_does_not_mutate_and_is_idempotent(self):
        source = {"data": {"default_quest_shape": "circle"}, "chapters": [{"filename": "stable", "quests": [
            {"id": "AAAAAAAAAAAAAAAA", "title": "A", "dependencies": [], "icon": {"id": "minecraft:book"}},
        ], "quest_links": [{"id": "4444444444444444", "linked_quest": "AAAAAAAAAAAAAAAA", "x": 2, "y": 3}]}]}
        original = json.loads(json.dumps(source))
        once = renderer.normalize_manifest(source)
        self.assertEqual(source, original)
        self.assertEqual(once, renderer.normalize_manifest(once))

    def test_edge_through_unrelated_node_and_collinear_overlap_are_reported(self):
        chapter = {"quests": [
            {"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 4, "y": 0, "dependencies": ["a"]},
            {"id": "middle", "x": 2, "y": 0.4, "size": 1.0},
            {"id": "c", "x": 1, "y": 0, "dependencies": ["a"]},
            {"id": "d", "x": 3, "y": 0, "dependencies": ["c"]},
            {"id": "shared", "x": 0, "y": 4}, {"id": "far", "x": 0, "y": 8, "dependencies": ["shared"]},
            {"id": "near", "x": 0, "y": 6, "dependencies": ["shared"]},
        ]}
        metrics = renderer.graph_metrics(chapter)
        self.assertGreaterEqual(metrics["visible_edge_through_unrelated_nodes"], 1)
        self.assertGreaterEqual(metrics["visible_edge_overlaps"], 1)
        self.assertGreaterEqual(metrics["visible_edge_crossings"], 1)

    def test_frontier_render_manifest_has_all_chapters_and_clean_geometry(self):
        manifest_path = Path(__file__).parents[1] / "docs/frontier/render-manifest.json"
        if not manifest_path.exists():
            self.skipTest("Frontier render manifest is optional in a minimal checkout")
        manifest = renderer.normalize_manifest(json.loads(manifest_path.read_text(encoding="utf-8")))
        self.assertEqual(len(manifest["chapters"]), 9)
        self.assertTrue(any(chapter.get("quest_links") for chapter in manifest["chapters"]),
                        "Frontier maps must retain native cross-chapter links")
        for chapter in manifest["chapters"]:
            metrics = renderer.graph_metrics(chapter)
            self.assertEqual(metrics["node_overlaps"], 0, chapter.get("filename"))
            self.assertEqual(metrics["estimated_label_collisions"], 0, chapter.get("filename"))
            self.assertEqual(metrics["visible_edge_crossings"], 0, chapter.get("filename"))
            self.assertEqual(metrics["visible_edge_through_unrelated_nodes"], 0, chapter.get("filename"))
            self.assertEqual(metrics["visible_edge_overlaps"], 0, chapter.get("filename"))
            self.assertEqual(metrics["missing_dependency_nodes"], 0, chapter.get("filename"))
            # Encounter and order boards may show several prerequisite lanes;
            # global welcome reachability is enforced by the semantic audit.
            # Every displayed node must nevertheless participate in a line.
            nodes = renderer.render_quests(chapter)
            connected = {dep for q in nodes for dep in q.get("dependencies", [])}
            connected.update(q["id"] for q in nodes if q.get("dependencies"))
            self.assertEqual(connected, {q["id"] for q in nodes}, chapter.get("filename"))
            self.assertEqual(metrics["quest_link_errors"], [], chapter.get("filename"))
        complete = renderer.chapters_from_root(
            Path(__file__).parents[1] / "config/ftbquests/quests")
        self.assertEqual(len(complete["chapters"]), 14)
        for chapter in complete["chapters"]:
            metrics = renderer.graph_metrics(chapter)
            for key in ("missing_dependency_nodes", "node_overlaps",
                        "visible_edge_crossings", "visible_edge_through_unrelated_nodes"):
                self.assertEqual(metrics[key], 0, (chapter.get("filename"), key))

    def test_backdrop_outside_quest_bounds_remains_in_frame(self):
        chapter = {"quests": [{"id": "a", "x": 0, "y": 0}], "images": [
            {"x": 12, "y": 8, "width": 20, "height": 12},
        ]}
        for detail in (False, True):
            width, height, _, point = renderer.chapter_viewport(chapter, detail)
            left, top = point(2, 2)
            right, bottom = point(22, 14)
            self.assertGreater(left, 0)
            self.assertGreater(top, 70)
            self.assertLess(right, width)
            self.assertLess(bottom, height)

    def test_large_backdrop_expands_canvas_without_shrinking_quest_spacing(self):
        quests = [{"id": "a", "title": "Alpha", "x": -4, "y": 0},
                  {"id": "b", "title": "Beta", "x": 4, "y": 0}]
        plain = {"quests": quests}
        illustrated = {"quests": quests, "images": [
            {"x": 20, "y": 0, "width": 24, "height": 16, "rotation": 0},
        ]}
        plain_width, plain_height, plain_scale, plain_point = renderer.chapter_viewport(plain)
        art_width, art_height, art_scale, art_point = renderer.chapter_viewport(illustrated)
        self.assertGreater(art_width, plain_width)
        self.assertGreater(art_height, plain_height)
        self.assertAlmostEqual(art_scale, plain_scale)
        self.assertAlmostEqual(art_point(4, 0)[0] - art_point(-4, 0)[0],
                               plain_point(4, 0)[0] - plain_point(-4, 0)[0])

    def test_chapter_default_and_explicit_false_override(self):
        chapter = {"default_hide_dependency_lines": True, "quests": [
            {"id": "a", "title": "A", "x": 0, "y": 0},
            {"id": "b", "title": "B", "x": 2, "y": 0, "dependencies": ["a"]},
            {"id": "c", "title": "C", "x": 4, "y": 0, "dependencies": ["b"], "hide_dependency_lines": False},
        ]}
        chapter["quests"] = [renderer.normalize_quest(q) for q in chapter["quests"]]
        self.assertTrue(renderer.effective_hidden(chapter, chapter["quests"][1]))
        self.assertFalse(renderer.effective_hidden(chapter, chapter["quests"][2]))
        metrics = renderer.graph_metrics(chapter)
        self.assertEqual(metrics["hidden_dependency_edges"], 1)
        self.assertEqual(metrics["visible_edge_count"], 1)


    def test_shapes_and_sizes_are_preserved(self):
        chapter = {"title": "01 · Test", "filename": "test", "quests": [
            {"id": "a", "title": "Alpha", "x": 0, "y": 0, "shape": "hexagon", "size": 1.6},
            {"id": "b", "title": "Beta", "x": 5, "y": 0, "shape": "square", "size": 1.0, "dependencies": ["a"]},
        ]}
        self.assertIsNotNone(renderer.shape_points("hexagon", (0, 0), 20))
        self.assertIsNotNone(renderer.shape_points("square", (0, 0), 20))
        metrics = renderer.graph_metrics(chapter)
        self.assertEqual(metrics["visible_edge_count"], 1)
        self.assertEqual(metrics["hidden_dependency_edges"], 0)
        self.assertEqual(metrics["estimated_label_collisions"], 0)

        far = {"quests": [
            {"id": "left", "title": "A long title", "x": -20, "y": 0},
            {"id": "right", "title": "Another long title", "x": 20, "y": 0},
        ]}
        self.assertEqual(renderer.graph_metrics(far)["estimated_label_collisions"], 0)


    def test_snbt_baseline_reader_and_deterministic_labels(self):
        source = '''{ default_hide_dependency_lines: true quests: [ { id: "a" title: "A very long quest title that must wrap" x: 0 y: 0 } { id: "b" title: "B" x: 3 y: 0 dependencies: ["a"] hide_dependency_lines: false } ] title: "Test" }'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "chapters").mkdir(); (root / "chapters" / "test.snbt").write_text(source, encoding="utf-8")
            loaded = renderer.chapters_from_root(root)
            self.assertEqual(len(loaded["chapters"]), 1)
            chapter = loaded["chapters"][0]
            self.assertFalse(renderer.effective_hidden(chapter, chapter["quests"][1]))
            self.assertGreater(len(renderer.wrap_lines(chapter["quests"][0]["title"], renderer.ImageDraw.Draw(renderer.Image.new("RGB", (1, 1))), renderer.font(18), 140)), 1)
            with tempfile.TemporaryDirectory() as out:
                first, _ = renderer.render_chapter(chapter, {}, {}, set(), set(), Path(out), 0, True)
                first_bytes = first.read_bytes()
                second, _ = renderer.render_chapter(chapter, {}, {}, set(), set(), Path(out), 0, True)
                self.assertEqual(first_bytes, second.read_bytes())
