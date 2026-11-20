# Website editing guide

For the everyday write → preview → publish steps and one-time setup, see the [README](../Readme.md). Blog posts are ordinary MyST Markdown files; Manim is only needed to create new visualizations.

## Posts and assets

Keep one post per `.md` file directly in `website/posts/`, starting with a `# Title`. All posts are discovered automatically and sorted by filename in reverse order. Use `YYYY-MM-DD-title.md` for chronological ordering. Dates are a naming convention, not a publication schedule. Keep drafts outside `website/`.

Keep each post's assets in `website/posts/assets/<post-name>/`. This directory is excluded from page discovery, so a Markdown download or supporting notes will not become an extra page. Referenced images and downloads are copied automatically by Sphinx; commit their source files with the post.

```markdown
![A useful description](assets/my-post/figure.png)

[Download data](assets/my-post/data.csv)

{download}`Download Markdown notes <assets/my-post/notes.md>`
```

Use the explicit `{download}` role for a Markdown source download, since an ordinary link to `.md` normally means another website page. Use relative Markdown links for other posts, for example `[Earlier post](2026-11-08-why-cross-entropy-penalizes-confident-mistakes.md)`.

Use fenced code blocks for syntax highlighting:

````markdown
```python
print("Hello")
```
````

Use `$...$` for inline LaTeX mathematics and `$$...$$` for display mathematics. Use lowercase filenames with hyphens and relative asset paths. A missing image, download, or page reference fails the strict website build.

For example, a display equation can occupy one line:

```markdown
$$ f(x) = y^2$$
```

For longer expressions, put the opening and closing `$$` on separate lines. Keep a blank line before and after each display equation. MyST parses the LaTeX and MathJax typesets it in the browser; you do not need a TeX installation to build the blog.

## Paper reviews

Write one review per Markdown file directly in `website/paper-reviews/`, using `YYYY-MM-DD-paper-title.md`. A `# Title` and your review text are sufficient. The optional [paper review template](../templates/paper-review.md) includes a citation, the central idea, the evidence, your assessment, and follow-up questions.

Reviews are discovered automatically, listed newest filename first, and included in navigation. The archive shows a reading-log introduction until the first review is added. New, renamed, and deleted reviews also refresh the index during native incremental Sphinx builds.

Put assets in `website/paper-reviews/assets/<paper-title>/`. Images, downloads, code blocks, and mathematics use the same syntax as blog posts. Asset Markdown is excluded from page discovery. Keep unfinished reviews outside `website/`; a filename date does not delay publication. Commit the review and its assets, then push to `main` to publish.

## Build and preview

This is a Sphinx website. You can build it directly using the standard Sphinx CLI:

```sh
source .venv/website/bin/activate
sphinx-build -b dirhtml -W --keep-going -n website _site
python -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Open http://localhost:8000/. Rerun `sphinx-build` after an edit and refresh the browser. The equivalent module command is `python -m sphinx -b dirhtml -W --keep-going -n website _site`. Use the `dirhtml` builder to match the deployed directory-style URLs. `-W` treats warnings as failures, `--keep-going` reports all warnings, and `-n` checks references strictly.

Sphinx builds incrementally in the output directory; obsolete files can remain after a deletion or rename. The repository's optional helper provides clean builds and preserves the previous working output on failure:

```sh
python3 scripts/website.py build
python3 scripts/website.py preview
```

The preview command builds first and serves http://localhost:8000/. Keep it running; after another edit, run `build` in a second terminal and refresh the browser. Press Ctrl+C to stop. Use `preview --port 8001` if port 8000 is occupied.

The helper uses `.venv/website` when available, otherwise the current Python installation. Each build starts fresh, so removed or renamed posts and assets disappear from output. Failed builds leave the previous successful output in place. `_site/` is generated and ignored by Git. `build --output /path/to/output` can select another output directory; the helper refuses to overwrite a nonempty directory without its generated `.nojekyll` marker.

Commit completed changes and push to `main`. GitHub Actions runs the tests and the same build command before deploying to GitHub Pages. Pull requests run checks and build without deploying. Documentation-only edits do not trigger deployment.

## Site design

The website uses locally bundled Inter variable fonts for running text, including a true italic companion, and navigation. Geist is used for headings, titles, and subtitles. MathJax keeps mathematics in its TeX math font. The page background stays white, including on devices that prefer dark mode.

The site menu always shows Home, Blog posts, Paper reviews, Visualizations, and About in the same order. It does not expand differently depending on the current page. Individual posts and reviews remain automatically listed in their section indexes. Breadcrumbs link back to Home and parent sections; Furo's separate “On this page” outline lists headings within the current article. On phones, the menu button opens the same site navigation.

Edit `website/_static/website.css` for the layout and typography, `website/_templates/` for the theme overrides, and `website/index.md` for the homepage. Ordinary posts inherit the design automatically. Font sources and licenses are recorded in `website/_static/fonts/NOTICE.txt`. Existing visualization media and its in-frame typography are retained.

## Edit a visualization page or card

Open its Markdown file, for example `website/samples/xor-forward-pass.md`. The YAML block at the top controls the card and player; the text underneath is the page explanation:

```markdown
---
title: 'XOR: inside a forward pass'
description: Trace an input through ReLU and sigmoid.
task: xor-forward-pass
media: assets/xor-forward-pass/visualization.mp4
thumbnail: assets/xor-forward-pass/thumbnail.png
alt: A two-input XOR network with activation graphs.
order: 40
width: 1920
height: 1080
---

Your explanation goes here. Inline mathematics uses $h=\max(0,z)$.
```

Change `title`, `description`, `alt`, optional `subtitle`, `order`, or the explanation, then build. The title becomes the page heading automatically. Lower `order` numbers appear first; omitted ordering sorts after numbered cards, by filename. There is no separate catalog to maintain and no video HTML to write. The player and back link are inserted during the build; download controls stay hidden.

Review your explanation against the animation before committing. Building checks links, metadata and reviewed media, not the scientific truth of prose. If an explanation changes what the animation is supposed to demonstrate, update the render requirements and review the output again.

The `task`, `media`, `thumbnail`, `width`, and `height` fields connect to the reviewed render. Keep them unchanged for a text edit. Replacing media or changing render requirements/source still requires the [render review workflow](visualization-workflow.md).

## Add a visualization card

After its render task is reviewed, run:

```sh
python3 scripts/website.py publish tasks/my-example
```

This copies approved media and creates `website/samples/my-example.md`. Edit that one Markdown file and build; the card and navigation are discovered automatically. Subsequent media publication preserves your authored title, summary, ordering and explanation. If the new render changes the explanation, update the page yourself as part of its review.

You can also create the Markdown file yourself using the format above, referencing an existing matching reviewed task and its published assets. A new Manim animation still needs its own render and review; copying Markdown does not generate a new animation.

A non-render concept card must explicitly use `kind: concept`, have a thumbnail and the usual text metadata, and cannot reference Manim task assets. It is labeled as a concept preview. A failed Manim render cannot be converted into a concept card to bypass its review.

## Add an ordinary page

Create `website/my-page.md`:

```markdown
# My page

Write your content here.
```

Add `my-page` to the existing toctree in `website/index.md` if it should appear in the main navigation. Ordinary pages do not need render-task metadata.

## Where to edit

| Change | File |
| --- | --- |
| About text | `website/about.md` |
| Homepage | `website/index.md` |
| Blog post | `website/posts/<date>-<title>.md` |
| Paper review | `website/paper-reviews/<date>-<paper-title>.md` |
| Sample title, card summary or explanation | `website/samples/<id>.md` |
| Animation request, source or reviewed explanation snapshot | `tasks/<id>/` |

The task's `content.md` is the reviewed explanation snapshot used to seed a new page. It stays covered by that task's review hash. For everyday website edits, use the Markdown file in `website/`; changing a task snapshot requires re-review and does not overwrite an existing authored page.
