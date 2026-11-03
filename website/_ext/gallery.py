"""Integrate the reviewed gallery catalog with the Sphinx build."""

import json
import runpy
import shutil
from pathlib import Path

from sphinx.errors import ExtensionError


def catalog(app):
    return json.loads((Path(app.srcdir) / "samples" / "catalog.json").read_text())


def validate_reviews(app):
    workflow = Path(app.srcdir).parent / "scripts" / "visualization_workflow.py"
    runpy.run_path(str(workflow))["check_published"]()
    for sample in catalog(app):
        page = Path(app.srcdir) / "samples" / f"{sample['id']}.md"
        thumbnail = Path(app.srcdir) / "samples" / sample["thumbnail"]
        if not page.is_file() or not thumbnail.is_file():
            raise ExtensionError(f"Gallery item {sample['id']} needs a detail page and thumbnail")


def insert_gallery(app, docname, source):
    if docname != "samples/index":
        return
    app.env.note_dependency(str(Path(app.srcdir) / "samples" / "catalog.json"))
    entries = catalog(app)
    lines = ["::::{grid} 1 1 2 3", ":gutter: 3", ""]
    for sample in entries:
        lines.extend([
            f":::{{grid-item-card}} {sample['title']}",
            f":link: {sample['id']}", ":link-type: doc",
            f":img-top: {sample['thumbnail']}", f":img-alt: {sample['alt']}",
            ":class-card: sample-card", "",
        ])
        if sample.get("subtitle"):
            lines.extend([f"**{sample['subtitle']}**", ""])
        lines.extend([sample["description"], ""])
        if sample["kind"] == "concept":
            lines.extend(["+++", "Concept preview", ""])
        lines.extend([":::", ""])
    lines.extend(["::::", "", "```{toctree}", ":hidden:", ""])
    lines.extend(sample["id"] for sample in entries)
    lines.extend(["```", ""])
    source[0] = source[0].replace("<!-- gallery -->", "\n".join(lines))


def finish_build(app, exception):
    if exception is not None or app.builder.format != "html":
        return
    output = Path(app.outdir)
    # Keep existing /samples/assets/ links and downloads available. Sphinx also
    # creates its own image copies for Markdown figures and card thumbnails.
    shutil.copytree(Path(app.srcdir) / "samples" / "assets", output / "samples" / "assets", dirs_exist_ok=True)
    (output / ".nojekyll").touch()
    (output / "samples.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0;url=samples/">'
        '<link rel="canonical" href="samples/"><title>Sample visualizations</title>'
        '</head><body><a href="samples/">View sample visualizations</a></body></html>\n'
    )


def setup(app):
    app.connect("builder-inited", validate_reviews)
    app.connect("source-read", insert_gallery)
    app.connect("build-finished", finish_build)
    return {"version": "1.0", "parallel_read_safe": True}
