"""Discover paper reviews and keep the empty archive valid in strict builds."""

INDEX = 'paper-reviews/index'


def update_index(app, env, added, changed, removed):
    if any(name.startswith('paper-reviews/') and name != INDEX
           for name in added | changed | removed):
        return [INDEX]
    return []


def insert_reviews(app, docname, source):
    if docname != INDEX:
        return
    reviews = sorted((name.removeprefix('paper-reviews/') for name in app.env.found_docs
                      if name.startswith('paper-reviews/') and name != INDEX
                      and name.count('/') == 1), reverse=True)
    if reviews:
        lines = ['```{toctree}', ':maxdepth: 1', ':titlesonly:', '', *reviews, '```']
        content = '\n'.join(lines)
    else:
        content = 'The reading log begins here. Reviews will appear as I work through the papers.'
    source[0] = source[0].replace('<!-- paper-reviews -->', content)


def setup(app):
    app.connect('env-get-outdated', update_index)
    app.connect('source-read', insert_reviews)
    return {'version': '1.0', 'parallel_read_safe': True}
