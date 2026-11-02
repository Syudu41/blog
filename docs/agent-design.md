# Agent: design discussion

Status: proposal, not an implemented generation agent.

## Agreed direction

- Audience: ML researchers.
- Benchmark topic: neural network forward propagation and backpropagation. Detailed benchmark selection is deferred; a small hand-checkable network is preferred, with a batched tensor example as the second choice.
- Primary output: publication figures. Companion outputs: 1080p/30 fps video, PNG, and GIF.
- Existing project purpose: visualizations for presentations.
- Showcase: GitHub Pages, with source in `site/`.
- Initial interface: a local CLI producing editable Manim source and rendered assets.
- All mathematics in every output format must be authored and rendered through LaTeX. Running text uses Arial or a similar sans-serif family.

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

Confirmed typography: Arial or a similar sans-serif family for running text and prose labels. Every equation and other mathematical expression must use LaTeX across still images, animation frames, GIFs, and videos, including mathematical axis labels, tensor notation, and inline math. Do not substitute Unicode approximations or ordinary text rendering for mathematics. A specific LaTeX math font is still undecided; Latin Modern is a proposed default. Use monospace only for literal code, not as a replacement for mathematical typesetting.

[Manim's text guide](https://docs.manim.community/en/stable/guides/using_text.html) distinguishes Pango-backed `Text` from LaTeX-backed `Tex`/`MathTex`. Install and pin fonts in the render environment; check availability and missing glyphs before rendering. Keep font licenses with distributed files, reject silent substitution, and match equation sizes optically across the two pipelines.

Use `Text` for prose and `Tex`/`MathTex` for all mathematical content. Keep LaTeX source editable alongside the scene source. Select and record an available Arial-family font explicitly during setup; use an appropriately licensed alternative if Arial is unavailable. Existing website concept SVGs predate this agent rendering standard and are not compliant Manim output examples.

## Pipeline and logistics

Version one is a local CLI. Its output bundle should include editable Manim Python, LaTeX source/templates, rendered assets, and a reproducibility manifest. The public website remains the showcase. Model provider, CLI command syntax, and installation method remain to be decided.

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

Selection is deferred. The following is a provisional design for the preferred small-network option, not a requirement to choose or implement the benchmark now.

Use a small fully connected network with explicit dimensions, activation, and loss. Verify forward values and gradients using an independent numerical/autodiff calculation. Show chain-rule flow and distinguish parameter gradients from activation gradients. Deliver a publication panel sequence, matching animation, and accessible textual explanation. Validate that selected ManimML primitives support the required semantics; implement custom scenes where needed.

## Questions for the next discussion

1. Which target venue/figure width should we match? Running text is already set to the Arial family; all mathematics uses LaTeX.
2. Revisit benchmark details when ready, beginning with the preferred hand-checkable small network and considering batched tensors second.
3. Should video be silent with captions or narrated? Which language/voice?
4. For the local CLI, which model provider and cost/render-time budgets are available?
5. Should publication require review, or should selected categories publish automatically?
