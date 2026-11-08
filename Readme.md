# Sudarshan's Blog

Sudarshan Balaji's personal blog about machine learning, mathematics, research, and ideas worth exploring.

[Visit the blog](https://syudu41.github.io/blog/) · [Posts](https://syudu41.github.io/blog/posts/) · [About](https://syudu41.github.io/blog/about/) · [Visualizations](https://syudu41.github.io/blog/samples/)

## Write a new post

1. Create one Markdown file in `website/posts/`, named `YYYY-MM-DD-your-title.md`. For example, `2026-11-08-my-first-post.md`.
2. Add a title, date, and your content:

   ```markdown
   # My first post

   *Sudarshan Balaji · 8 November 2026*

   Introduce the question you want to explore.

   ## A small example

   Inline mathematics: $h=\max(0,z)$.

   $$
   \mathcal L=-\ln p
   $$

   Explain what the equation means and work through an example.
   ```

3. Preview the post, then commit and push it as described below.

Posts appear automatically in the **Blog posts** index and navigation, newest filename first. There is no index file to update for each post. The filename date controls ordering; pushing a future-dated post still publishes it immediately. Keep unfinished drafts outside `website/`.

For a complete example, see the [sample post source](website/posts/2026-11-08-why-cross-entropy-penalizes-confident-mistakes.md) or [read it online](https://syudu41.github.io/blog/posts/2026-11-08-why-cross-entropy-penalizes-confident-mistakes/).

## Preview locally

Run these once if website dependencies are not installed:

```sh
python3 -m venv .venv/website
.venv/website/bin/python -m pip install -r website/requirements.txt
```

From the repository root:

```sh
python3 scripts/website.py preview
```

Open http://localhost:8000/posts/. After editing, run `python3 scripts/website.py build` in a second terminal and refresh the browser. Stop the preview server with Ctrl+C.

## Publish

For the example filename above:

```sh
git add website/posts/2026-11-08-my-first-post.md
git commit -m "Add my first blog post."
git push origin main
```

GitHub Actions builds the site and publishes it to GitHub Pages. Check the repository's **Actions** tab for the deployment result. Build output in `_site/` is generated locally and does not need to be committed.

You can also write directly on GitHub: open `website/posts/`, choose **Add file → Create new file**, use the dated filename, write the Markdown, and commit to `main`. Deployment then runs automatically.

## Add images and code

Put a post's images in `website/posts/assets/my-first-post/` and reference them with a relative path:

```markdown
![A useful description of the figure](assets/my-first-post/figure.png)
```

Commit the image files along with the post. Use fenced code blocks, such as three backticks followed by `python`, for syntax-highlighted code. Mathematics uses LaTeX inside `$...$` or `$$...$$`.

The site uses Sphinx, MyST Markdown, and Furo. See the [website editing guide](docs/website.md) for other pages and visualization cards. The repository also retains the source and review evidence for the visualization gallery.
