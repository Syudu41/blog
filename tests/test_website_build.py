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

from scripts.visualization_workflow import prepare_review, publish, write_json, gallery_entries, split_page, write_page

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


class SiteNavigation(HTMLParser):
    """Read the visible site menu independently of article section outlines."""

    def __init__(self, page):
        super().__init__()
        self.page = page
        self.in_menu = False
        self.anchor = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'nav' and attrs.get('aria-label') == 'Site navigation':
            self.in_menu = True
        if self.in_menu and tag == 'a':
            self.anchor = [attrs['href'], '']

    def handle_data(self, data):
        if self.anchor is not None:
            self.anchor[1] += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor is not None:
            href, label = self.anchor
            path = unquote(urlsplit(href).path)
            target = (self.page.parent / path).resolve() if path else self.page.resolve()
            if target.is_dir():
                target /= 'index.html'
            self.links.append((label.strip(), target))
            self.anchor = None
        if tag == 'nav':
            self.in_menu = False


@unittest.skipUnless(importlib.util.find_spec("sphinx"), "Install website/requirements.txt for website integration tests")
class WebsiteBuildTests(unittest.TestCase):
    def test_reviewed_image_video_math_and_legacy_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "website", root / "website")
            (root / "scripts").mkdir()
            shutil.copyfile(ROOT / "scripts/visualization_workflow.py", root / "scripts/visualization_workflow.py")
            shutil.copyfile(ROOT / "scripts/website.py", root / "scripts/website.py")
            existing = gallery_entries(root / "website/samples")
            for sample in existing:
                if sample.get("kind") == "render":
                    shutil.copytree(ROOT / "tasks" / sample["task"], root / "tasks" / sample["task"],
                                    ignore=shutil.ignore_patterns("runs", "__pycache__"))
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
            command = [sys.executable, str(root / "scripts/website.py"), "build", "--output", str(output)]
            # The native Sphinx CLI builds the same site without our convenience wrapper.
            result = subprocess.run([sys.executable, '-m', 'sphinx', '-b', 'dirhtml', '-W',
                                     '--keep-going', '-n', str(root / 'website'), str(output)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            expected_menu = [
                ('Home', output / 'index.html'),
                ('Blog posts', output / 'posts/index.html'),
                ('Paper reviews', output / 'paper-reviews/index.html'),
                ('Visualizations', output / 'samples/index.html'),
                ('About', output / 'about/index.html'),
            ]
            for page in output.rglob("*.html"):
                parser = LocalLinks(page)
                parser.feed(page.read_text())
                for target in parser.targets:
                    self.assertTrue(target.is_file(), f"Broken local link in {page}: {target}")
                if page.name != 'samples.html':
                    navigation = SiteNavigation(page)
                    navigation.feed(page.read_text())
                    self.assertEqual(navigation.links, expected_menu, f'Inconsistent site menu: {page}')
            about = (output / 'about/index.html').read_text()
            self.assertIn('aria-label="Breadcrumb"', about)
            self.assertIn('class="prev-page"', about)
            about_article = about.split('<article', 1)[1].split('</article>', 1)[0]
            for link in ('../posts/', '../paper-reviews/', '../samples/'):
                self.assertIn(f'href="{link}"', about_article)
            gallery = (output / "samples/index.html").read_text()
            expected_cards = len(gallery_entries(root / "website/samples"))
            self.assertEqual(gallery.count('class="sd-card-title'), expected_cards)
            for slug in [sample["id"] for sample in gallery_entries(root / "website/samples")]:
                self.assertTrue((output / "samples" / slug / "index.html").is_file())
            self.assertIn('url=samples/', (output / "samples.html").read_text())
            video = (output / "samples/video-fixture/index.html").read_text()
            self.assertIn('src="../assets/video-fixture/visualization.mp4"', video)
            self.assertIn('poster="../assets/video-fixture/thumbnail.svg"', video)
            self.assertIn('controlslist="nodownload"', video)
            for sample in gallery_entries(root / "website/samples"):
                page = (output / "samples" / sample["id"] / "index.html").read_text()
                self.assertNotIn("Download visualization", page)
            self.assertIn('class="math', video)
            self.assertIn("mathjax", video.lower())
            self.assertIn('dataset.theme = "light"', video)
            self.assertTrue((output / "searchindex.js").is_file())
            self.assertTrue((output / ".nojekyll").is_file())
            self.assertIn('The reading log begins here.',
                          (output / 'paper-reviews/index.html').read_text())
            # A post, images and downloadable assets need no configuration edits.
            posts = root / "website/posts"
            assets = posts / "assets" / "fixture"
            assets.mkdir(parents=True)
            (assets / "plot.svg").write_text(svg)
            (assets / "data.csv").write_text("x,y\n1,2\n")
            # Asset Markdown must not become a separate website page.
            (assets / "notes.md").write_text("This is a downloadable source file.\n")
            plain = posts / "plain-title.md"
            plain.write_text(
                "# Plain filename fixture\n\n"
                "![Test plot](assets/fixture/plot.svg)\n\n"
                "[Download data](assets/fixture/data.csv)\n\n"
                "{download}`Download notes <assets/fixture/notes.md>`\n\n"
                "```python\nprint('hello')\n```\n"
            )
            older = posts / "2090-01-01-fixture-older.md"
            newer = posts / "2091-01-01-fixture-newer.md"
            older.write_text("# Older post fixture\n\nA temporary test post.\n")
            newer.write_text("# Newer post fixture\n\nInline math: $x^2$.\n\n$$ f(x) = y^2$$\n")
            added_posts = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(added_posts.returncode, 0, added_posts.stdout + added_posts.stderr)
            post_index = (output / "posts/index.html").read_text()
            self.assertLess(post_index.index("2091-01-01-fixture-newer/"),
                            post_index.index("2090-01-01-fixture-older/"))
            self.assertTrue((output / "posts/2091-01-01-fixture-newer/index.html").is_file())
            math_page = (output / "posts/2091-01-01-fixture-newer/index.html").read_text()
            self.assertIn('class="math notranslate nohighlight"', math_page)
            self.assertIn(r'\[ f(x) = y^2\]', math_page)
            self.assertIn("plain-title/", post_index)
            self.assertTrue((output / "posts/plain-title/index.html").is_file())
            self.assertFalse((output / "posts/assets/fixture/notes/index.html").exists())
            for page in output.rglob("*.html"):
                parser = LocalLinks(page)
                parser.feed(page.read_text())
                for target in parser.targets:
                    self.assertTrue(target.is_file(), f"Broken local link in {page}: {target}")
            self.assertTrue(any(path.read_text() == "x,y\n1,2\n" for path in (output / "_downloads").rglob("data.csv")))
            # A bad edit must fail and leave the last successful preview available.
            before = (output / "posts/plain-title/index.html").read_bytes()
            plain.write_text("# Broken post\n\n![Missing figure](assets/missing.png)\n")
            broken = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(broken.returncode, 0)
            self.assertEqual((output / "posts/plain-title/index.html").read_bytes(), before)
            plain.unlink()
            shutil.rmtree(assets)
            older.unlink()
            newer.unlink()
            removed_posts = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(removed_posts.returncode, 0, removed_posts.stdout + removed_posts.stderr)
            self.assertNotIn("fixture-newer/", (output / "posts/index.html").read_text())
            self.assertNotIn("fixture-older/", (output / "posts/index.html").read_text())
            self.assertFalse((output / "posts/plain-title").exists())
            self.assertFalse((output / "posts/2091-01-01-fixture-newer").exists())
            self.assertFalse(list((output / "_downloads").rglob("data.csv")))
            # Custom output must never erase authored files or source directories.
            protected = root / "notes"
            protected.mkdir()
            (protected / "keep.md").write_text("Keep my notes.")
            for target in (protected, root, root / "website", root / "website/posts"):
                refused = subprocess.run(command[:-1] + [str(target)], capture_output=True, text=True)
                self.assertNotEqual(refused.returncode, 0)
            self.assertEqual((protected / "keep.md").read_text(), "Keep my notes.")
            # Editing the authored Markdown updates the player page and card
            # without changing the immutable render task or review.
            page_path = root / "website/samples/video-fixture.md"
            metadata, body = split_page(page_path.read_text())
            metadata.update(title="Edited video title", description="Edited card description")
            write_page(page_path, metadata, body + "\n\nA new human-authored paragraph.")
            edited = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(edited.returncode, 0, edited.stdout + edited.stderr)
            self.assertIn("Edited video title", (output / "samples/index.html").read_text())
            self.assertIn("A new human-authored paragraph", (output / "samples/video-fixture/index.html").read_text())
            # Adding a Markdown file discovers a card on an incremental build.
            (root / "website/samples/assets/incremental.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><circle r="2"/></svg>')
            extra = {"title": "Incremental fixture", "thumbnail": "assets/incremental.svg", "alt": "Test circle.",
                     "description": "A synthetic test preview.", "kind": "concept"}
            extra_page = root / "website/samples/incremental-fixture.md"
            write_page(extra_page, extra, "A new sample.")
            incremental = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(incremental.returncode, 0, incremental.stdout + incremental.stderr)
            self.assertEqual((output / "samples/index.html").read_text().count('class="sd-card-title'), expected_cards + 1)
            self.assertTrue((output / "samples/incremental-fixture/index.html").is_file())
            extra_page.unlink()
            removed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(removed.returncode, 0, removed.stdout + removed.stderr)
            self.assertEqual((output / "samples/index.html").read_text().count('class="sd-card-title'), expected_cards)
            # Review discovery must also update a native incremental Sphinx build.
            reviews = root / 'website/paper-reviews'
            review_assets = reviews / 'assets/fixture'
            review_assets.mkdir(parents=True)
            (review_assets / 'notes.md').write_text('Supporting notes, not a website page.\n')
            first = reviews / '2090-01-01-first-paper.md'
            latest = reviews / '2091-01-01-latest-paper.md'
            first.write_text('# First paper review\n\nMy first reading note.\n')
            latest.write_text('# Latest paper review\n\n$$ f(x) = y^2$$\n\n'
                              '{download}`Supporting notes <assets/fixture/notes.md>`\n')
            native = [sys.executable, '-m', 'sphinx', '-b', 'dirhtml', '-W',
                      '--keep-going', '-n', str(root / 'website'), str(output)]
            added_reviews = subprocess.run(native, capture_output=True, text=True)
            self.assertEqual(added_reviews.returncode, 0, added_reviews.stdout + added_reviews.stderr)
            review_index = (output / 'paper-reviews/index.html').read_text()
            self.assertLess(review_index.index('2091-01-01-latest-paper/'),
                            review_index.index('2090-01-01-first-paper/'))
            self.assertNotIn('The reading log begins here.', review_index)
            self.assertFalse((output / 'paper-reviews/assets/fixture/notes/index.html').exists())
            review_page = output / 'paper-reviews/2091-01-01-latest-paper/index.html'
            parser = LocalLinks(review_page)
            parser.feed(review_page.read_text())
            for target in parser.targets:
                self.assertTrue(target.is_file(), f'Broken review link: {target}')
            first.unlink()
            latest.unlink()
            removed_reviews = subprocess.run(native, capture_output=True, text=True)
            self.assertEqual(removed_reviews.returncode, 0, removed_reviews.stdout + removed_reviews.stderr)
            review_index = (output / 'paper-reviews/index.html').read_text()
            self.assertIn('The reading log begins here.', review_index)
            self.assertNotIn('2091-01-01-latest-paper/', review_index)
            self.assertNotIn('2090-01-01-first-paper/', review_index)
            # The actual Sphinx build must refuse output changed since its review.
            (root / "tasks/image-fixture/output.svg").write_text("unreviewed replacement")
            failed = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("changed after review", failed.stdout + failed.stderr)


if __name__ == "__main__":
    unittest.main()
