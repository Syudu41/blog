# Sudarshan's Blog

My personal blog about machine learning, mathematics, and research.

[Read the blog](https://syudu41.github.io/blog/) · [Paper reviews](https://syudu41.github.io/blog/paper-reviews/) · [About](https://syudu41.github.io/blog/about/) · [Visualizations](https://syudu41.github.io/blog/samples/)

## Set up once

```sh
python3 -m venv .venv/website
.venv/website/bin/python -m pip install -r website/requirements.txt
```

Blog writing only needs these website dependencies. The existing visualization gallery and its rendering tools are retained separately.

## Add a post

Create `website/posts/2026-11-19-my-post.md`:

```markdown
# My post

*Sudarshan Balaji · 19 November 2026*

Write your explanation here. Inline mathematics: $h=\max(0,z)$.

$$ f(x) = y^2$$

![Description of my figure](assets/my-post/figure.png)

[Download the data](assets/my-post/data.csv)
```

Put the accompanying files in `website/posts/assets/my-post/`. Omit the image and download links when you have no assets. No front matter, task folder, or index edit is needed.

Every `.md` file directly inside `website/posts/` appears automatically. Use `YYYY-MM-DD-title.md` to list dated posts newest first; plain filenames also work and sort by filename. Use lowercase names with hyphens for posts and assets. Keep drafts outside `website/`; future dates do not delay publication.

## Add a paper review

Create `website/paper-reviews/YYYY-MM-DD-paper-title.md`, or start with the optional template:

```sh
cp templates/paper-review.md website/paper-reviews/2026-11-19-paper-title.md
```

Replace the title, reading date, citation, and prompts with your review. Put any accompanying assets in `website/paper-reviews/assets/paper-title/` and link them as `assets/paper-title/figure.png`. Reviews appear automatically in **Paper reviews**, newest filename first. No index edit is needed, and the section stays valid when empty.

Use the same preview and publishing steps below, staging your review and its assets instead of a blog post.

## Preview and publish

From the repository root, activate the website environment and build with Sphinx:

```sh
source .venv/website/bin/activate
sphinx-build -b dirhtml -W --keep-going -n website _site
python -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Open http://localhost:8000/. After an edit, rerun the Sphinx command in another terminal with the same environment activated, then refresh. Stop the server with Ctrl+C. `dirhtml` produces the directory-style URLs used by the live site, and `-W -n` makes broken references fail the build.

For a clean build after removing or renaming a post, use `python3 scripts/website.py build`. This convenience wrapper runs the same Sphinx builder in a temporary directory, removes obsolete output, and keeps the last successful preview when a build fails. `python3 scripts/website.py preview` combines that clean build with the local server.

When the preview looks right:

```sh
python3 scripts/website.py build
git add website/posts/2026-11-19-my-post.md website/posts/assets/my-post/
git commit -m "Add my post."
git push origin main
```

Omit the assets path from `git add` for a text-only post. GitHub Actions checks, builds, and deploys pushes to `main`; pull requests run checks without deployment. Check the repository's **Actions** tab for the result. Generated `_site/` output stays out of Git.

You can also add the Markdown file and upload its assets directly on GitHub, then commit to `main`.

See the [website guide](docs/website.md) for code blocks, downloads, other pages, and the retained visualization workflow. The site uses Sphinx, MyST Markdown, and Furo, with a white background, Inter running text and navigation, Geist headings and subtitles, and LaTeX mathematics. Font files are served locally with their licenses in `website/_static/fonts/`. Every page has the same five-link site menu; breadcrumbs provide a route back to Home and the current section.
