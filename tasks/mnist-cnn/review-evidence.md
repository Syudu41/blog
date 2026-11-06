# MNIST CNN review evidence

## Computation and provenance

The animation uses original MNIST test index 0 (target 7), declared before model
training, with pixels divided by 255. The dataset archive SHA256 is recorded in
training.json. Training uses original training indices 0:55000, validation
55000:60000, seed 2026, CPU PyTorch 2.5.1, four epochs of Adam at 0.001, batch 128.
All 4,266 weights and biases, the image and each intermediate tensor are retained
in trace.npz. No training or update is depicted in the video.

Commands:

```sh
.venv/render/bin/python tasks/mnist-cnn/train.py /tmp/tensorquill-mnist.npz
.venv/render/bin/python tasks/mnist-cnn/verify_numerics.py /tmp/tensorquill-mnist.npz
```

An independent float64 NumPy implementation reconstructs both cross-correlations
(including zero padding, biases and channel sums), ReLU, both max pools, flatten,
linear logits and softmax. The largest absolute tensor discrepancy from the
float32 training framework is 1.069e-6; probability discrepancy is 4.44e-12.
Independent sample cross-entropy is 1.09210477e-5. Exported-logit float64 display
cross-entropy is 1.09210521e-5; both round to the displayed 1.0921e-5.
A separately reconstructed model reproduces 9,688 correct predictions out of
10,000 test examples (96.88%) and test mean cross-entropy 0.1012110182.
See numerical-verification.json and training.json for actual values and splits.

## Draft inspection and corrections

The successful 960x540, 15 fps draft was fully decoded: 1,223 frames, 81.533 s.
Twenty-three samples covered every teaching hold, four scan positions and three
transitions. Feature-map pixel comparisons passed for all first/second-layer
channels and pooling outputs (95th-percentile channel error at most 8/255).
The coding agent inspected all six draft contact sheets at 960px per frame.

Corrections incorporated before the final render:

- Remove the kernel and multiplication symbol after revealing products, so the
  transition does not imply applying the kernel twice.
- Enlarge the ReLU result into two readable lines below the weighted sum.
- Show flattening as a single-column representation of all 392 activations.
- Give the second pooling its own heading and caption; remove the first-layer
  context when focusing on pooling the eight second-layer channels.
- Avoid misleading negative-zero numerical labels in rounded matrices.

Manim 0.19's image camera failed with Pillow 13; environment.yml now pins the
compatible Pillow 11.3.0. Heatmap raster dimensions are equalized for interpolation
between different spatial resolutions while preserving nearest-neighbor pixels.
These were rendering failures, not accepted output; successful media is reviewed
separately below.

## Final render and review

Final native render command:

```sh
TENSORQUILL_TEX_BIN=/home/lab335a/Sudarshan/Research-PhD/visualizer/.venv/tex/bin/x86_64-linux \
python3 -m tensorquill render tasks/mnist-cnn --python .venv/render/bin/python --preset final --timeout 1500
.venv/render/bin/python tasks/mnist-cnn/checks.py
```

Run 20261106T161023Z-e2dd07 exited successfully and played 88 Manim animations.
The complete MP4 decodes to 2,469 frames, 1920x1080, 30 fps, 82.3 seconds,
H264/yuv420p, 5,351,408 bytes. SHA256:
`b8a718496b3f475898f5308a7a0386f1975c817ae7bf20d9453b736b55f9bc45`.
The reviewer inspected all six final contact sheets (review-stages-1..6.png),
23 samples at 960px per frame: all teaching holds, four moving scan positions,
and three transitions. Also inspected the enlarged ReLU frame separately.

checks.py independently verifies the enlarged convolution and pooling result,
all probability-bar values, ordering of the teaching stages, safe object bounds,
pure black frame corners, full media decoding, and actual heatmap pixels for
all four first-layer channels, all eight second-layer channels and pooled maps.
The worst 95th-percentile channel discrepancy is 6/255. A once-per-second bitmap
check of the constant title shows under 1% thresholded pixel change, confined
to codec edge variation. All these checks passed; see review-verification.json.
The thumbnail is extracted from the completed four-feature-map hold.

### Explanatory assessment

The image and target establish a concrete recognition question. A receptive-field
highlight becomes the normalized patch; learned weights produce nine products,
then a sum with bias. The separately enlarged ReLU result follows the sum;
a negative response elsewhere is explicitly distinguished from this selected
positive response. The scanning input and output highlights maintain spatial
correspondence and build the computed channel. Four maps generalize the single
kernel operation. Pooling highlights an actual maximum, then second-convolution
notation explicitly sums over all four channels. Eight computed channels are
pooled before their 392 values are reshaped into a single-column display.
Logits precede softmax, and sample loss is separate from full-test-set accuracy.

Objects remain stable inside each explanation; caption changes fade sequentially.
The revised ReLU is readable, labels have whitespace, and no overlays obscure the
feature maps. All numerical annotations and equations use MathTex; prose is
Liberation Sans. Holds provide reading time and the final prediction is held for
five seconds. The video is an original TensorQuill inference explanation; no
training, backpropagation, or filter-semantics claim is implied.

A first browser review caught native paused controls obscuring the lowest
caption. Captions were moved up to scene y=-2.85, followed by a complete new
render, re-decoding, all numerical/color/layout checks and inspection of all 23
current samples. This review covers the revised artifact above.

Website integration is checked after the approved local publication build and
before committing and deploying; results are in website-verification.json.

## Website verification

Strict Sphinx/Furo build and published-artifact integrity check passed. All 27
repository tests passed. Playwright/Chrome played the revised video at desktop
and mobile sizes: the player stayed 736x414 and 358x201.375 pixels respectively
before and during playback, with no overflow, media errors or page exceptions.
The page remains white with Arial/Helvetica prose, the gallery card exists, and
no download links appear. Inspected review-website.png: the raised caption sits
above the native paused playback buttons. Fullscreen remains available for the
technical annotations. Reproduce with:

```sh
python3 scripts/website.py build
.venv/website/bin/python tasks/mnist-cnn/check_website.py
.venv/website/bin/python -m unittest discover -s tests
.venv/website/bin/python scripts/visualization_workflow.py check
```
