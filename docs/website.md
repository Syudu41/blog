# Edit and build the website

Edit Markdown in `website/`. You do not need Manim or a coding agent to change a page's text, card title, or summary.

From the repository root:

```sh
python3 scripts/website.py build
python3 scripts/website.py preview
```

The preview command builds first and serves http://localhost:8000/. Keep it running; after another edit, run `build` in a second terminal and refresh the browser. Press Ctrl+C to stop. Use `preview --port 8001` if port 8000 is occupied.

The helper uses `.venv/website` when available. For a new installation, install the website dependencies once:

```sh
python3 -m venv .venv/website
.venv/website/bin/python -m pip install -r website/requirements.txt
```

Commit completed changes and push to `main`. GitHub Actions uses the same build command to deploy the website.

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
| Sample title, card summary or explanation | `website/samples/<id>.md` |
| Animation request, source or reviewed explanation snapshot | `tasks/<id>/` |

The task's `content.md` is the reviewed explanation snapshot used to seed a new page. It stays covered by that task's review hash. For everyday website edits, use the Markdown file in `website/`; changing a task snapshot requires re-review and does not overwrite an existing authored page.
