# Render, review, publish

Every Manim task lives in `tasks/<task-id>/`. The folder holds the request, editable scene source, output files, explanation, and review evidence. Copy `tasks/_template/` to start a task; replace its placeholders and add `scene.py` and `output/`.

```text
tasks/<task-id>/
  task.json          # Metadata, acceptance criteria, source and output paths
  requirements.md    # User request and detailed requirements
  scene.py           # Editable Manim source
  content.md         # Explanation for the website detail page
  output/            # Rendered media and card thumbnail
  review.json        # Results tied to these exact files
```

## Review every output

After rendering, run `python scripts/visualization_workflow.py prepare-review tasks/<task-id>`. This creates a pending review with hashes of the request, metadata, source, explanation, output, and thumbnail. It never marks tests as passed automatically.

The agent must open and inspect the generated output, compare it with every requirement, and run the relevant numerical and media checks. For animations, inspect representative frames and playback, including transitions and timing. For figures, inspect the image at its final intended size. Check both the output and thumbnail. Every generated revision needs a fresh review; archive the previous review before preparing another.

Record a pass/fail result and specific evidence for each requirement and each check in `review.json`:

- `render_success`: actual renderer command, exit status, and log or test result.
- `output_integrity`: decode the media and verify format, dimensions, duration/frame rate when applicable, and thumbnail validity. Record the tools and measured values.
- `mathematics`: compare calculations, labels, dimensions, and assumptions with independent calculations or tests. Explain when a check is not applicable.
- `latex_and_fonts`: confirm all math is rendered from LaTeX and prose uses the configured Arial-family font.
- `layout`: check clipping, label collisions, readability, and final-size presentation.
- `visual_review`: inspect the actual output against the requested visual behavior; record the frames or image examined and findings.

Set `status` to `passed` and record the reviewing agent only when every result passes with evidence. Fix failed output and review it again. The publication script validates recorded results and file hashes; it does not replace visual inspection, execute Manim, or independently prove mathematical correctness. Review evidence must describe checks that were actually performed.

## Wire passing output to the website

Run `python scripts/visualization_workflow.py publish tasks/<task-id>`. It refuses incomplete, failed, or stale reviews, then copies the reviewed media and thumbnail, creates the Sphinx/MyST detail page, and adds the gallery card. Use a distinct id from existing concept previews.

Install the website dependencies, then run `python -m unittest discover -s tests` and `python scripts/visualization_workflow.py check`. Build with `python -m sphinx -b dirhtml -W --keep-going -n website _site`. Inspect the resulting page before committing the task and its website integration together as a completed subfeature. Push the commit to deploy through GitHub Pages.

The Sphinx build also checks that published Manim renders still match their reviewed task files. Concept previews are explicitly labeled and are not represented as reviewed Manim outputs.

## Website structure

`website/` is the source folder. Sphinx builds the entire website with the Furo theme. MyST parses the Markdown pages, and Sphinx Design provides cards generated from `website/samples/catalog.json`. The directory-style HTML builder preserves `/samples/` and existing detail-page URLs. `/samples.html` remains a redirect for existing links. The website uses a white background and Arial-family text.

Install dependencies with `python -m pip install -r website/requirements.txt`, then use the Sphinx build command above. Preview the generated website with `python -m http.server 8000 --directory _site` and open http://localhost:8000/. Rebuild after source changes. GitHub Actions runs tests and builds the complete website before publishing.

Write inline mathematics as `$...$` and displayed mathematics as `$$...$$` or a MyST `math` directive. MyST parses the LaTeX expressions and Sphinx's MathJax extension typesets them in the browser. Math within Manim-rendered images and animations continues to use Manim's LaTeX pipeline. Keep the LaTeX source editable in both cases.
