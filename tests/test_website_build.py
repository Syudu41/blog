"""Check the built website and publication integration, not just source files."""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from scripts.visualization_workflow import prepare_review, publish, write_json

ROOT = Path(__file__).resolve().parents[1]


class LocalLinks(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.targets = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src") and value:
                url = urlsplit(value)
                if not url.scheme and not url.netloc and url.path:
                    target = (self.page.parent / unquote(url.path)).resolve()
                    if target.is_dir():
                        target /= "index.html"
                    self.targets.append(target)


@unittest.skipUnless(importlib.util.find_spec("sphinx"), "Install website/requirements.txt for website integration tests")
class WebsiteBuildTests(unittest.TestCase):
    def test_reviewed_image_video_math_and_legacy_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "website", root / "website")
            (root / "scripts").mkdir()
            shutil.copyfile(ROOT / "scripts/visualization_workflow.py", root / "scripts/visualization_workflow.py")
            for slug, suffix in (("image-fixture", ".svg"), ("video-fixture", ".mp4")):
                task = root / "tasks" / slug
                task.mkdir(parents=True)
                write_json(task / "task.json", {
                    "id": slug, "title": f"Fixture {slug}", "description": "Integration fixture.",
                    "alt": "Fixture visualization.", "source": "scene.py",
                    "output": "output" + suffix, "thumbnail": "thumbnail.svg",
                    "requirements": [{"id": "fixture", "description": "Check website wiring."}],
                })
                (task / "requirements.md").write_text("Website integration test fixture, not a real render.")
                (task / "scene.py").write_text("# Website integration fixture\n")
                (task / "content.md").write_text("Inline math: $x^2$.\n\n$$\\alpha + \\beta$$\n")
                svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle r="2"/></svg>'
                (task / "thumbnail.svg").write_text(svg)
                # These fixtures exercise link generation; no media decoding is claimed.
                (task / ("output" + suffix)).write_bytes(svg.encode() if suffix == ".svg" else b"test-video-fixture")
                prepare_review(task)
                review = json.loads((task / "review.json").read_text())
                review.update(status="passed", reviewer="integration-test")
                for group in ("requirements", "checks"):
                    for result in review[group].values():
                        result.update(passed=True, evidence="Website wiring fixture; not a media-quality review.")
                write_json(task / "review.json", review)
                publish(task, root)

            output = root / "build"
            command = [sys.executable, "-m", "sphinx", "-b", "dirhtml", "-W", "--keep-going", "-n", str(root / "website"), str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for page in output.rglob("*.html"):
                parser = LocalLinks(page)
                parser.feed(page.read_text())
                for target in parser.targets:
                    self.assertTrue(target.is_file(), f"Broken local link in {page}: {target}")
            gallery = (output / "samples/index.html").read_text()
            expected_cards = len(json.loads((root / "website/samples/catalog.json").read_text()))
            self.assertEqual(gallery.count('class="sd-card-title'), expected_cards)
            for slug in ("forward-pass", "gradient-descent", "linear-transformation", "image-fixture", "video-fixture"):
                self.assertTrue((output / "samples" / slug / "index.html").is_file())
            self.assertIn('url=samples/', (output / "samples.html").read_text())
            video = (output / "samples/video-fixture/index.html").read_text()
            self.assertIn('src="../assets/video-fixture/visualization.mp4"', video)
            self.assertIn('poster="../assets/video-fixture/thumbnail.svg"', video)
            self.assertIn('class="math', video)
            self.assertIn("mathjax", video.lower())
            self.assertIn('dataset.theme = "light"', video)
            self.assertTrue((output / "searchindex.js").is_file())
            self.assertTrue((output / ".nojekyll").is_file())
            # The actual Sphinx build must refuse output changed since its review.
            (root / "tasks/image-fixture/output.svg").write_text("unreviewed replacement")
            failed = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("changed after review", failed.stdout + failed.stderr)


if __name__ == "__main__":
    unittest.main()
