# Render, review, publish

For website text and cards, see [Edit and build the website](website.md). Those edits happen in `website/` and do not require rendering. This document covers producing and approving new Manim media.

## Keep a persistent render task

Every task lives in `tasks/<id>/`:

```text
task.json          # Render metadata and acceptance criteria
requirements.md    # Request and storyboard
scene.py           # Editable Manim scene
content.md         # Reviewed explanation snapshot for the render
output/            # Primary media and thumbnail
review.json        # Review evidence tied to exact task files
```

The coding agent can create the scaffold using `python -m tensorquill new <id> --request-file request.txt --format mp4`, then write the scene. The CLI does not write scene code itself. See [rendering](rendering.md) for environment setup and [agent responsibilities](agent-workflow.md) for what runs automatically.

Write a storyboard using [visual standards](visual-standards.md). Render a draft, inspect it, revise where necessary, and produce a final render. Inspect the actual animation, including transitions, pacing and final-size typography. Check every requirement and run independent mathematical checks where applicable.

## Review the exact output

Run:

```sh
python scripts/visualization_workflow.py prepare-review tasks/<id>
```

This creates a pending review; it never assumes a pass. Fill every requirement and every check with actual evidence:

- `render_success`: command, renderer exit status and report.
- `output_integrity`: full media decoding, dimensions, timing, codec and thumbnail checks.
- `mathematics`: independent calculations or a reason the check is inapplicable.
- `latex_and_fonts`: LaTeX mathematics and the configured Arial-family prose font.
- `layout`: clipping, collisions and readability at the intended display size.
- `visual_review`: inspected frames, transitions and findings against the storyboard.

Set `status: passed` and name the reviewer only when all requirements pass. Archive an existing review before preparing a new one. A change to requirements, source, the task's explanation snapshot, metadata, output or thumbnail invalidates that task review. Re-review the current output; rerender when its source or intended behavior changes.

## Publish approved media

```sh
python3 scripts/website.py publish tasks/<id>
python scripts/visualization_workflow.py check
python3 scripts/website.py build
```

Publication validates the review, copies media to `website/samples/assets/<id>/`, and creates a Markdown page with YAML card metadata if the page does not yet exist. It preserves an existing authored page's wording, title, summary and ordering. The agent must ensure that page still correctly explains any newly published render.

Sphinx builds cards automatically from those Markdown files. Its publication gate still rejects stale render reviews, changed task media, mismatched asset references and unsafe paths. Website prose is authored separately; review it against the visualization before committing. Build success does not certify arbitrary scientific claims in text.

Run the appropriate tests, inspect the built page, commit the completed feature, and push to deploy through GitHub Pages. All pages retain Sphinx, MyST and Furo, a white background, Arial-family prose and LaTeX mathematics.

A review JSON validates recorded evidence and file integrity. It does not replace scientific or visual inspection, and does not generate an animation or certify its explanatory quality automatically.
