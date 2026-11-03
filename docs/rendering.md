# Local rendering with TensorQuill

The coding agent reads the request and writes editable Manim scenes. The local CLI creates task folders, checks the rendering environment, runs scenes, and checks the resulting media. It does not call a language-model API or generate scene code by itself.

## Rendering environment

Use Python 3.11 with Manim Community 0.19.0 and ManimML 0.0.24. This pair uses the feed-forward adapter described below. `environment.yml` installs the Python/native rendering dependencies through conda-forge and pip:

```sh
micromamba create -y -p .venv/render -f environment.yml
python -m tensorquill doctor --python .venv/render/bin/python
```

Install a working TeX distribution separately. Manim needs both `latex` and `dvisvgm`, plus the `standalone`, `preview`, `babel-english`, `amsmath`, and `amsfonts` packages. On Debian/Ubuntu, a normal system setup can use `texlive-latex-base`, `texlive-latex-recommended`, `texlive-latex-extra`, `texlive-fonts-recommended`, and `dvisvgm`. Use an existing distribution or a portable [TinyTeX](https://yihui.org/tinytex/) installation when system installation is unavailable.

For a portable TeX installation outside PATH, set its binary directory explicitly:

```sh
export TENSORQUILL_TEX_BIN=/path/to/TinyTeX/bin/x86_64-linux
python -m tensorquill doctor --python .venv/render/bin/python
```

The doctor checks Manim's version, the exact font family, FFmpeg/FFprobe, and the TeX tools. It also compiles and converts a real LaTeX expression; executable presence alone is insufficient. Liberation Sans is the default Arial-compatible prose font. Install that family or select another available Arial-family font in `task.json`.

Rendering uses Cairo without a display or GPU. Scenes must be trusted local Python: a separate process and Python environment are not an operating-system sandbox. Docker access was unavailable on the development machine, so this implementation does not claim container isolation.

ManimML 0.0.24's network-level forward-pass helper creates empty animation groups that Manim 0.19 rejects. For fully connected feed-forward layers, use `from tensorquill.manimml import forward_pass`, then `self.play(forward_pass(network, run_time=3))`. The adapter composes ManimML's existing layer animations without the empty wrappers. It supports this specific layer family; convolutional, dropout, and other scene types need their own compatibility checks.

## Create and render a task

Write the user's request in a text file, then create its task folder:

```sh
python -m tensorquill new my-visualization --request-file request.txt --format png
```

The coding agent edits `tasks/my-visualization/scene.py`, the requirements, card description, accessible description, and `content.md`. The initial scene deliberately refuses to render until it is implemented. The scene class defaults to `Visualization`; change `render.scene` in `task.json` if needed.

```sh
python -m tensorquill render tasks/my-visualization --python .venv/render/bin/python --preset draft
python -m tensorquill render tasks/my-visualization --python .venv/render/bin/python --preset final
```

Each render creates `tasks/<id>/runs/<timestamp-id>/` with its inputs, settings, log, media report, output, thumbnail, and review images. Failed runs retain a failure report. The default timeout is 180 seconds; set `--timeout` explicitly for a longer scene. Timed-out worker process groups are stopped.

Drafts stay in their run folders. A successful final render of the task's primary format copies its artifact and thumbnail to the paths in `task.json`. Any prior review is archived into the run folder, requiring a new review. Task/source changes during rendering block final staging.

## Output presets

| Format | Final default | Draft default |
| --- | --- | --- |
| PNG | 1800 × 1200, 300 dpi metadata | 900 × 600 |
| MP4 | 1920 × 1080, 30 fps, H.264/yuv420p | 960 × 540, 15 fps |
| GIF | 960 × 540, 15 fps, looping | 480 × 270, up to 15 fps |

The PNG default corresponds to 6 × 4 inches at 300 dpi. Choose dimensions to suit the paper or presentation; it is not a venue-specific publication layout. Override `render.width`, `render.height`, `render.fps`, or `render.dpi` in `task.json`. Both video dimensions must be even. The maximum supported dimensions are 7680 × 7680 and 120 fps. Default artifact size limits are 100 MB, or 20 MB for GIF; override `render.max_bytes` explicitly.

For companion exports from the same scene:

```sh
python -m tensorquill render tasks/my-visualization --python .venv/render/bin/python --preset final --format mp4
python -m tensorquill render tasks/my-visualization --python .venv/render/bin/python --preset final --format gif
```

Companion formats stay in their run folders. The task's primary format remains the one specified by `task.output`; the publication gate reviews and publishes that primary artifact. To publish a different format, update the task requirements and output path, render it as the primary output, and review it again. Native PDF/SVG figure export is not implemented; a PNG is not a vector figure.

## Checks and review

The renderer decodes PNG/GIF images, fully decodes MP4, and checks dimensions, video frame rate, duration, codec, pixel format, and file size as applicable. It generates representative animation frames and a review sheet. Reports record settings, hashes, Python/packages, and native tool versions.

These checks prove media integrity, not scientific correctness. The agent must inspect each output, compare it with the request, and run independent mathematical checks where needed. For animations, check the frame sequence and timing as well as the representative frames. Follow [the review/publication workflow](visualization-workflow.md) only after those checks pass.

Manim renders happen locally; GitHub Pages serves approved static artifacts. The website deployment workflow does not render scenes or hold model credentials.
