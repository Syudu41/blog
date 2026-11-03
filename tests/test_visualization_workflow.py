import json
import tempfile
import unittest
from pathlib import Path

from scripts.visualization_workflow import check_published, prepare_review, publish, write_json


class PublicationGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.task = self.root / "tasks" / "test-render"
        self.task.mkdir(parents=True)
        gallery = self.root / "website" / "samples"
        gallery.mkdir(parents=True)
        write_json(gallery / "catalog.json", [])
        write_json(self.task / "task.json", {
            "id": "test-render", "title": "Test render", "description": "A test figure.",
            "alt": "A circle.", "source": "scene.py", "output": "figure.svg",
            "thumbnail": "figure.svg",
            "requirements": [{"id": "circle", "description": "Show a circle."}],
        })
        (self.task / "requirements.md").write_text("Show a circle, with no labels.")
        (self.task / "content.md").write_text("The figure shows a circle.")
        (self.task / "scene.py").write_text("# Editable scene fixture\n")
        (self.task / "figure.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><circle r="10"/></svg>')
        prepare_review(self.task)

    def approve(self):
        review = json.loads((self.task / "review.json").read_text())
        review.update(status="passed", reviewer="test-reviewer")
        for group in ("requirements", "checks"):
            for result in review[group].values():
                result.update(passed=True, evidence="Checked the fixture against the requested output.")
        write_json(self.task / "review.json", review)

    def test_pending_review_cannot_publish(self):
        with self.assertRaisesRegex(ValueError, "completed review"):
            publish(self.task, self.root)

    def test_each_requirement_needs_evidence(self):
        self.approve()
        review = json.loads((self.task / "review.json").read_text())
        review["requirements"]["circle"]["evidence"] = ""
        write_json(self.task / "review.json", review)
        with self.assertRaisesRegex(ValueError, "requirements.circle"):
            publish(self.task, self.root)

    def test_visual_review_cannot_be_skipped(self):
        self.approve()
        review = json.loads((self.task / "review.json").read_text())
        del review["checks"]["visual_review"]
        write_json(self.task / "review.json", review)
        with self.assertRaisesRegex(ValueError, "every checks"):
            publish(self.task, self.root)

    def test_changed_output_invalidates_review(self):
        self.approve()
        (self.task / "figure.svg").write_text("changed render")
        with self.assertRaisesRegex(ValueError, "changed after review"):
            publish(self.task, self.root)

    def test_changed_requirements_invalidate_review(self):
        self.approve()
        (self.task / "requirements.md").write_text("Show two circles.")
        with self.assertRaisesRegex(ValueError, "changed after review"):
            publish(self.task, self.root)

    def test_review_is_not_overwritten(self):
        with self.assertRaisesRegex(ValueError, "already exists"):
            prepare_review(self.task)

    def test_changed_explanation_invalidates_review(self):
        self.approve()
        (self.task / "content.md").write_text("An unreviewed explanation.")
        with self.assertRaisesRegex(ValueError, "changed after review"):
            publish(self.task, self.root)

    def test_existing_page_is_not_overwritten(self):
        self.approve()
        (self.root / "website/samples/test-render.md").write_text("An existing page.")
        with self.assertRaisesRegex(ValueError, "existing page"):
            publish(self.task, self.root)

    def test_approved_output_is_wired_to_gallery(self):
        self.approve()
        publish(self.task, self.root)
        check_published(self.root)
        page = self.root / "website/samples/test-render.md"
        self.assertIn("assets/test-render/visualization.svg", page.read_text())
        catalog = json.loads((self.root / "website/samples/catalog.json").read_text())
        self.assertEqual(catalog[0]["page"], "test-render/")

    def test_modified_published_asset_blocks_build(self):
        self.approve()
        publish(self.task, self.root)
        asset = self.root / "website/samples/assets/test-render/visualization.svg"
        asset.write_text("unreviewed replacement")
        with self.assertRaisesRegex(ValueError, "differs from reviewed"):
            check_published(self.root)

    def test_updating_a_sample_preserves_card_order(self):
        self.approve()
        publish(self.task, self.root)
        path = self.root / "website/samples/catalog.json"
        entries = json.loads(path.read_text())
        entries.append({"id": "later", "kind": "concept"})
        write_json(path, entries)
        publish(self.task, self.root)
        self.assertEqual([entry["id"] for entry in json.loads(path.read_text())], ["test-render", "later"])

    def test_missing_output_blocks_review(self):
        (self.task / "figure.svg").unlink()
        with self.assertRaisesRegex(ValueError, "Missing or unsafe"):
            publish(self.task, self.root)

    def test_source_outside_task_is_rejected(self):
        outside = self.root / "outside.py"
        outside.write_text("# outside")
        task = json.loads((self.task / "task.json").read_text())
        task["source"] = str(outside)
        write_json(self.task / "task.json", task)
        with self.assertRaisesRegex(ValueError, "unsafe"):
            publish(self.task, self.root)


if __name__ == "__main__":
    unittest.main()
