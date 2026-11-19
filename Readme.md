# Sudarshan's Blog

My personal blog about machine learning, mathematics, and research.

[Read the blog](https://syudu41.github.io/blog/) · [About](https://syudu41.github.io/blog/about/) · [Visualizations](https://syudu41.github.io/blog/samples/)

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

$$
\mathcal L=-\ln p
$$

![Description of my figure](assets/my-post/figure.png)

[Download the data](assets/my-post/data.csv)
```

Put the accompanying files in `website/posts/assets/my-post/`. Omit the image and download links when you have no assets. No front matter, task folder, or index edit is needed.

Every `.md` file directly inside `website/posts/` appears automatically. Use `YYYY-MM-DD-title.md` to list dated posts newest first; plain filenames also work and sort by filename. Use lowercase names with hyphens for posts and assets. Keep drafts outside `website/`; future dates do not delay publication.

## Preview and publish

From the repository root:

```sh
python3 scripts/website.py preview
```

Open http://localhost:8000/posts/. After an edit, run `python3 scripts/website.py build` in another terminal and refresh. Stop preview with Ctrl+C. Builds check references, remove obsolete output, and keep the last successful preview if the build fails.

When the preview looks right:

```sh
python3 scripts/website.py build
git add website/posts/2026-11-19-my-post.md website/posts/assets/my-post/
git commit -m "Add my post."
git push origin main
```

Omit the assets path from `git add` for a text-only post. GitHub Actions checks, builds, and deploys pushes to `main`; pull requests run checks without deployment. Check the repository's **Actions** tab for the result. Generated `_site/` output stays out of Git.

You can also add the Markdown file and upload its assets directly on GitHub, then commit to `main`.

See the [website guide](docs/website.md) for code blocks, downloads, other pages, and the retained visualization workflow. The site uses Sphinx, MyST Markdown, and Furo, with a white background, Arial-family text, and LaTeX mathematics.
