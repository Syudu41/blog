# Visualizer

This is a visualization tool based on ManimML, 3Blue1Brown standards. 

> [!TIP]
> This was created for the sole purpose to show visualizations during presentations. 

## Website

The static site lives in `site/`: About (`index.html`) and Sample visualizations (`samples.html`). The SVGs are original concept studies, not outputs from a working Manim agent. No build dependencies are required.

Preview with `python3 -m http.server 8000 --directory site`, then open http://localhost:8000.

The workflow `.github/workflows/pages.yml` publishes only `site/` on relevant pushes to `main` or manual dispatch. Repository Settings → Pages uses **GitHub Actions** as the publishing source. The production address after successful deployment is https://syudu41.github.io/visualizer/.

## Agent design

See [the design discussion](docs/agent-design.md) for agreed priorities, proposed visual standards, fonts, export presets, and open questions. The generation agent is currently in design; publication figures are the main quality bar, with 1080p video, PNG, and GIF as companion outputs.

