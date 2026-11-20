"""Build the complete website with Sphinx, MyST Markdown, and Furo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "_ext"))

project = "Sudarshan's Blog"
author = "Sudarshan Balaji"
copyright = "2026, Sudarshan Balaji"
extensions = ["myst_parser", "sphinx_design", "sphinx.ext.mathjax", "gallery", "paper_reviews"]
source_suffix = {".md": "markdown"}
root_doc = "index"
exclude_patterns = ["_build", "_ext", "_static", "_templates", "posts/assets/**", "paper-reviews/assets/**"]
myst_enable_extensions = ["colon_fence", "dollarmath", "amsmath"]
html_theme = "furo"
html_title = "Sudarshan's Blog"
html_baseurl = "https://syudu41.github.io/blog/"
html_static_path = ["_static"]
html_css_files = ["website.css"]
templates_path = ["_templates"]
html_show_sourcelink = False
html_copy_source = False
html_theme_options = {
    "light_css_variables": {
        "font-stack": '"Inter", Arial, sans-serif',
        "font-stack--headings": '"Geist", "Inter", Arial, sans-serif',
        "color-background-primary": "#ffffff",
        "color-background-secondary": "#ffffff",
    },
}
