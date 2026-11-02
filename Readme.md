# Visualizer

This is a visualization tool based on ManimML, 3Blue1Brown standards. 

> [!TIP]
> This was created for the sole purpose to show visualizations during presentations. 

## Website

The website uses the Minima Jekyll theme with a white background and Arial text. Its two pages live in `site/index.md` and `site/samples.md`. GitHub Actions builds `site/` with Jekyll and deploys the generated `_site/` directory to GitHub Pages.

To preview locally with Ruby and Bundler installed, run `cd site`, `bundle install`, then `bundle exec jekyll serve --baseurl /visualizer`. Open http://localhost:4000/visualizer/.

## Agent design

See [the design discussion](docs/agent-design.md) for agreed priorities, proposed visual standards, fonts, export presets, and open questions. The generation agent is currently in design; publication figures are the main quality bar, with 1080p video, PNG, and GIF as companion outputs.

