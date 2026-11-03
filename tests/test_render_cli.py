import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tensorquill.cli import create_task, render_task, run_worker, safe_path, settings_for, worker_environment


class RenderCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.folder = create_task("render-test", "Explain a square.", root=self.root)

    def fake_render(self, command, log, timeout):
        run = log.parent
        (run / "visualization.png").write_bytes(b"fixture-image")
        (run / "thumbnail.png").write_bytes(b"fixture-thumbnail")
        (run / "result.json").write_text(json.dumps({
            "status": "passed", "artifact": "visualization.png", "thumbnail": "thumbnail.png",
        }))
        return 0

    def test_new_task_preserves_request_and_refuses_overwrite(self):
        self.assertIn("Explain a square.", (self.folder / "requirements.md").read_text())
        self.assertIn("NotImplementedError", (self.folder / "scene.py").read_text())
        with self.assertRaises(FileExistsError):
            create_task("render-test", "Another request", root=self.root)

    def test_task_paths_cannot_escape(self):
        with self.assertRaises(ValueError):
            safe_path(self.folder, "../outside.png")

    def test_draft_leaves_final_output_and_review_untouched(self):
        output = self.folder / "output/visualization.png"
        output.parent.mkdir()
        output.write_bytes(b"previous-final")
        review = self.folder / "review.json"
        review.write_text("previous-review")
        with patch("tensorquill.cli.run_worker", side_effect=self.fake_render):
            render_task(self.folder)
        self.assertEqual(output.read_bytes(), b"previous-final")
        self.assertEqual(review.read_text(), "previous-review")

    def test_final_stages_output_and_requires_a_new_review(self):
        review = self.folder / "review.json"
        review.write_text("previous-review")
        with patch("tensorquill.cli.run_worker", side_effect=self.fake_render):
            run = render_task(self.folder, preset="final")
        self.assertEqual((self.folder / "output/visualization.png").read_bytes(), b"fixture-image")
        self.assertFalse(review.exists())
        self.assertEqual((run / "review.previous.json").read_text(), "previous-review")

    def test_failed_render_never_stages_output(self):
        with patch("tensorquill.cli.run_worker", return_value=1):
            with self.assertRaisesRegex(ValueError, "Render failed"):
                render_task(self.folder, preset="final")
        self.assertFalse((self.folder / "output").exists())
        self.assertEqual(len(list((self.folder / "runs").glob("*/failure.json"))), 1)

    def test_companion_export_keeps_primary_review(self):
        review = self.folder / "review.json"
        review.write_text("previous-review")
        with patch("tensorquill.cli.run_worker", side_effect=self.fake_render):
            render_task(self.folder, preset="final", output_format="mp4")
        self.assertTrue(review.exists())
        self.assertFalse((self.folder / "output").exists())

    def test_changing_input_during_render_blocks_final(self):
        def changed(command, log, timeout):
            (self.folder / "requirements.md").write_text("Different requirements")
            return self.fake_render(command, log, timeout)
        with patch("tensorquill.cli.run_worker", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "input changed"):
                render_task(self.folder, preset="final")
        self.assertFalse((self.folder / "output").exists())

    def test_nonpositive_or_odd_video_dimensions_are_rejected(self):
        for width in (0, -100, 1279):
            task = {"output": "output/video.mp4", "render": {"width": width}}
            with self.assertRaises(ValueError):
                settings_for(task, "final")

    def test_render_process_does_not_inherit_credentials(self):
        with patch.dict("os.environ", {"GITHUB_TOKEN": "test-token", "OPENAI_API_KEY": "test-key"}):
            env = worker_environment("/usr/bin/python3")
        self.assertNotIn("GITHUB_TOKEN", env)
        self.assertNotIn("OPENAI_API_KEY", env)

    def test_timeout_kills_the_render_process_group(self):
        with patch("tensorquill.cli.subprocess.Popen") as start, patch("tensorquill.cli.os.killpg") as kill:
            process = start.return_value
            process.pid = 12345
            process.wait.side_effect = [subprocess.TimeoutExpired("render", 1), 0]
            with self.assertRaisesRegex(ValueError, "exceeded"):
                run_worker(["/usr/bin/python3", "scene.py"], self.root / "timeout.log", 1)
            kill.assert_called_once()


if __name__ == "__main__":
    unittest.main()
