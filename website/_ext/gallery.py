"""Build cards and players from authored Markdown and validate reviewed media."""

import runpy
import shutil
from pathlib import Path

from sphinx.errors import ExtensionError


def workflow(app):
    return runpy.run_path(str(Path(app.srcdir).parent / 'scripts' / 'visualization_workflow.py'))


def catalog(app):
    return workflow(app)['gallery_entries'](Path(app.srcdir) / 'samples')


def validate_reviews(app):
    try:
        workflow(app)['check_published'](Path(app.srcdir).parent)
    except (ValueError, KeyError, OSError, TypeError) as error:
        raise ExtensionError(str(error)) from error


def update_gallery(app, env, added, changed, removed):
    # A new/edited/deleted Markdown card must refresh even an incremental build.
    if any(name.startswith('samples/') and name != 'samples/index' for name in added | changed | removed):
        return ['samples/index']
    return []


def insert_gallery(app, docname, source):
    entries = catalog(app)
    if docname != 'samples/index':
        if docname in {f"samples/{entry['id']}" for entry in entries}:
            source[0] = workflow(app)['render_page'](source[0])
        return
    lines = ['::::{grid} 1 1 2 3', ':gutter: 3', '']
    for sample in entries:
        app.env.note_dependency(str(Path(app.srcdir) / 'samples' / f"{sample['id']}.md"))
        lines.extend([
            f":::{{grid-item-card}} {sample['title']}",
            f":link: {sample['id']}", ':link-type: doc',
            f":img-top: {sample['thumbnail']}", f":img-alt: {sample['alt']}",
            ':class-card: sample-card', '',
        ])
        if sample.get('subtitle'):
            lines.extend([f"**{sample['subtitle']}**", ''])
        lines.extend([sample['description'], ''])
        if sample['kind'] == 'concept':
            lines.extend(['+++', 'Concept preview', ''])
        lines.extend([':::', ''])
    lines.extend(['::::', '', '```{toctree}', ':hidden:', ''])
    lines.extend(sample['id'] for sample in entries)
    lines.extend(['```', ''])
    source[0] = source[0].replace('<!-- gallery -->', '\n'.join(lines))


def finish_build(app, exception):
    if exception is not None or app.builder.format != 'html':
        return
    output = Path(app.outdir)
    shutil.copytree(Path(app.srcdir) / 'samples' / 'assets', output / 'samples' / 'assets', dirs_exist_ok=True)
    (output / '.nojekyll').touch()
    (output / 'samples.html').write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0;url=samples/">'
        '<link rel="canonical" href="samples/"><title>Sample visualizations</title>'
        '</head><body><a href="samples/">View sample visualizations</a></body></html>\n'
    )


def setup(app):
    app.connect('builder-inited', validate_reviews)
    app.connect('env-get-outdated', update_gallery)
    app.connect('source-read', insert_gallery)
    app.connect('build-finished', finish_build)
    return {'version': '2.0', 'parallel_read_safe': True}
