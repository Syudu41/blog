# Final review

Approved artifact: 107.867 seconds, 1920 × 1080, 30 fps, H264/yuv420p.
Current web MP4 SHA256: `ce1051276597c42b5b965ca292ddb76e905f871d60a2d39e5317399006682234`.

Commands:

```sh
.venv/render/bin/python tasks/pixel-pattern-mlp/train.py
.venv/render/bin/python tasks/pixel-pattern-mlp/verify_numerics.py
TENSORQUILL_TEX_BIN="$PWD/.venv/tex/bin/x86_64-linux" python3 -m tensorquill render tasks/pixel-pattern-mlp --python .venv/render/bin/python --preset final --timeout 1500
.venv/render/bin/python tasks/pixel-pattern-mlp/check_output.py tasks/pixel-pattern-mlp/runs/20261106T180342Z-8f461d
```

The first draft exposed black matrix brackets, cramped entries, a checkpoint synchronization issue and backward pulses continuing through the inactive ReLU. These were corrected before the final render. The explained image is explicitly part of the declared 128-image training set. All 40 first-step gradients agree with independent scalar finite differences; forward values and held-out scores are independently reconstructed. Training is float64; labels are rounded. The 64-image held-out toy score does not measure general natural-image performance.

Reviewed 12 final stage images in `review-frames/sheet-0.jpg` through `sheet-3.jpg`, plus temporal samples at +0.12, +0.38, +0.72 and +1.02 seconds of selected forward, output-error backward, gated hidden backward and replay transitions. Forward teal pulses travel from pixels toward classes; amber backward pulses travel toward hidden neurons, and only three active hidden neurons send pulses farther left. The selected matrix entry and incoming edge identify the same weight. The network remains the main visual; no plots cover its layers. The final thumbnail is extracted from the actual completed state. `review-frames/motion.webp` is a sparse accelerated review aid, not the published animation.

`layout.json` records actual matrix entry strings, node labels, bar widths, white brackets, edge geometry and object bounds. `check_output.py` validates them against the trace and checks all matrix entries are separated. It fully decodes the MP4. These checks supplement sampled visual inspection; they do not claim an exhaustive human inspection of every video frame.

The exact rendered headline and gradient LaTeX sources were recompiled with retained DVI in `/tmp/tensorquill-font-audit` to inspect font names. `font-verification.json` records source hashes and actual Computer Modern fonts. Other labels use the same templates. This video's CMR choice is the user's explicit override; website text remains unchanged.

The supplied YouTube reference is *Convolutional Neural Networks*, Computational Thinking. Its public maximum-resolution thumbnail was inspected. YouTube blocked full playback and download with traffic/sign-in checks. The scene uses the visible black canvas, Computer Modern text and teal/pink numerical emphasis; no claim is made about unseen reference transitions. This example is a dense MLP, not a convolutional network.

## Web streaming recheck

The original approved MP4 stored its `moov` index after its video data. It was remuxed with FFmpeg `-map 0 -c copy -movflags +faststart`. No frames were re-encoded. The original and optimized files have identical FFmpeg `framemd5` output for all 3,236 frames and timestamps. The index is now ahead of the video data. `streaming-verification.json` records box offsets, hashes, codec, duration and full decode results. `output-verification.json` was regenerated from the optimized file; the numerical checks, 27 repository tests, stage images and original explanatory criteria still pass. The review hashes now refer to this exact optimized file. The renderer worker applies the same packaging to future MP4 outputs.
