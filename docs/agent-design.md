# Agent: design discussion

Status: proposal, not an implemented generation agent.

## Agreed direction

- Audience: ML researchers.
- Benchmark: neural network forward propagation and backpropagation.
- Primary output: publication figures. Companion outputs: 1080p/30 fps video, PNG, and GIF.
- Existing project purpose: visualizations for presentations.
- Showcase: GitHub Pages, with source in `site/`.

## Engine and references

Start with Manim Community. [ManimML](https://github.com/helblazer811/ManimML) targets Community; pin a tested compatible pair before implementation rather than assuming the latest versions work together. Curate version-tested patterns from the [Community Gallery](https://docs.manim.community/en/stable/examples.html), retaining required license notices for reused code.

[3Blue1Brown's engine](https://github.com/3b1b/manim) is ManimGL, a separate codebase. Study the explanatory approach and [video scenes](https://github.com/3b1b/videos), while keeping APIs separate. Older scenes may require old dependencies. The standards proposed here are our design interpretation, not an official 3Blue1Brown specification. Review licenses per reused source or asset.

## Visual standards

- Establish the question, show a concrete example, reveal the mechanism, and connect it to the formalism. Give each scene one clear learning objective.
- Preserve object identity through transformations. Use consistent encodings for activations, parameters, and gradients, with labels and line styles alongside color.
- Label tensor shapes, units, assumptions, and schematic simplifications. Prefer direct labels over detached legends.
- Compose publication figures at their intended physical width. Start with 8–10 pt labels at final size, subject to venue rules. Review an actual-size proof. Make a separate layout for video rather than shrinking a video frame into a paper figure.
- Support a light paper theme and a dark presentation theme. Test contrast in both, inspect grayscale output, and keep consistent stroke weights.
- Use motion to show causality, pause on key states, and keep labels attached to objects. Provide static equivalents.

## Fonts

Proposed defaults: Source Sans 3 for labels/prose, Latin Modern through LaTeX for equations, and monospace only for code or literal values. Add a serif preset if a target venue requires it. These are proposals, not claims about 3Blue1Brown's fonts.

[Manim's text guide](https://docs.manim.community/en/stable/guides/using_text.html) distinguishes Pango-backed `Text` from LaTeX-backed `Tex`/`MathTex`. Install and pin fonts in the render environment; check availability and missing glyphs before rendering. Keep font licenses with distributed files, reject silent substitution, and match equation sizes optically across the two pipelines.

## Pipeline and logistics

1. Capture the concept, audience, assumptions/data, tensor dimensions, target physical size/venue, desired formats, duration, and narration needs.
2. Produce a structured storyboard with mathematical invariants, equations, object identities, and export presets.
3. Retrieve compatible patterns and generate editable scene source.
4. Execute Python in an isolated render worker with bounded resources, restricted network/filesystem access, and pinned Python, Manim, ManimML, fonts, LaTeX, and FFmpeg. Keep deployment credentials out of the worker.
5. Render a draft, then inspect representative frames and actual-size figures for mathematical errors, clipping, label collisions, timing, and contrast. Use a bounded correction loop; a successful render alone is insufficient.
6. Export artifacts plus a manifest recording the prompt/spec, source, dependencies, fonts, seeds, settings, timings, licenses, and artifact hashes.
7. Publish selected assets and metadata to GitHub Pages. Rendering and model API calls run separately; Pages presents static outputs.

Set per-job limits for duration, resolution, runtime, memory, retries, cost, and file size. Cache identical scene specifications. Keep intermediates outside Git and publish only selected web-sized assets; use artifact storage as the gallery grows.

## Export presets

| Output | Proposed standard |
| --- | --- |
| Paper figure | Target physical width; PNG at 300 dpi or venue requirement. Evaluate true PDF/SVG export for the selected scene pipeline before promising vector output. Wrapping raster frames in SVG does not make them vector figures. |
| Image | PNG at explicit dimensions; light/dark and optional transparency presets validated for the target output. |
| Video | MP4 H.264, 1920×1080, 30 fps, 16:9; 720p drafts. Poster image and captions/transcript when narrated. |
| GIF | Short loop with reduced dimensions/frame rate and optimized palette; explicit size budget and MP4 alternative. |

## First benchmark acceptance criteria

Use a small fully connected network with explicit dimensions, activation, and loss. Verify forward values and gradients using an independent numerical/autodiff calculation. Show chain-rule flow and distinguish parameter gradients from activation gradients. Deliver a publication panel sequence, matching animation, and accessible textual explanation. Validate that selected ManimML primitives support the required semantics; implement custom scenes where needed.

## Questions for the next discussion

1. Which target venue/figure width and existing paper fonts should we match?
2. Should the benchmark use a hand-checkable scalar toy network or a small batched tensor example?
3. Should video be silent with captions or narrated? Which language/voice?
4. Should version one be a local CLI, notebook workflow, or API service? Which model provider and cost/render-time budgets are available?
5. Should publication require review, or should selected categories publish automatically?
