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
