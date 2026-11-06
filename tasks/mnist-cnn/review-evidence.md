# Native ManimML CNN: final review

The user requested a visual CNN with layers and metrics, then specifically asked
for the ManimML/3Blue1Brown reference approach. Inspected the actual ManimML CNN
and image-fed CNN GIFs and their native layer/filter source. The final scene uses
ManimML Convolutional2DLayer, MaxPooling2DLayer, FeedForwardLayer and Filters.
Upright translucent vector planes and coupled orange receptive-field volumes
replace the mathematical slides and the unapproved tilted raster-stack experiment.

## Model and numerical evidence

The trained model and frozen trace are unchanged. MNIST test image 0 has target 7;
pixels are divided by 255. Training: original training indices 0:55000, validation
55000:60000, seed 2026, four epochs of Adam at0.001,batch128. Original test split:
10000 images. Trace and training metadata hashes are asserted before rendering.

Re-ran verify_numerics.py against the original dataset archive. Independent
float64 NumPy reconstruction verifies padded cross-correlations, channel sums,
biases, ReLU, both max pools, flattening, logits and softmax. Maximum tensor
error from float32 inference:1.069e-6; probabilities:4.44e-12. Independently
reconstructed full-test evaluation reproduces9688/10000 correct (96.88%) and
mean cross-entropy0.1012110182. Sample confidence rounds to99.9989%; sample
cross-entropy rounds to1.0921e-5. See numerical-verification.json and training.json.

Native blue planes communicate channel geometry and operation state. They do
not pretend to be per-pixel activation heatmaps. The input grayscale, flattened
activation bands, live scalar responses and output probabilities use actual
saved data. Uniform plane colors therefore carry no fabricated numerical claim.

## Draft inspection

Inspected layout previews against ManimML's actual reference frames, followed by
all seven native draft contact sheets (27 samples at960px/frame). Corrected a
native dense-layer z-order issue before the movie: nodes are above the black
surrounding rectangle. Reduced camera perspective so projected planes have
safe margins, and separated the compact Flatten/Dense labels. Live readouts are
initialized to the actual origin response, and padded windows are positioned
correctly before they fade in. Initial and final response holds allow reading.

Draft checks verify actual native types, channel counts, physical plane sides,
window dimensions, stride/padding, per-channel pooling, all live responses,
rendered orange field positions and winner-node visibility. A zero-extent
ValueTracker point is not rendered; it was excluded from projected-object bounds.
This was a review-record correction, not ignored clipping of a visible object.

## Final render and review

```sh
TENSORQUILL_TEX_BIN=/home/lab335a/Sudarshan/Research-PhD/visualizer/.venv/tex/bin/x86_64-linux \
python3 -m tensorquill render tasks/mnist-cnn --python .venv/render/bin/python --preset final --timeout 1500
.venv/render/bin/python tasks/mnist-cnn/checks.py
.venv/render/bin/python tasks/mnist-cnn/verify_numerics.py /tmp/tensorquill-mnist.npz
```

Run20261106T171538Z-6a0d52 exited0,85animations. Complete media decode:
1806frames,1920x1080,30fps,H264/yuv420p,60.2seconds,6284349bytes.
SHA256:2d986b2ec95219c2572d4cc7e15634936064b06c7867fffed85a643ed0a3e51f.

The reviewer inspected all seven final sheets (review-stages-1..7.png), including
27 teaching holds, motion samples and transitions, plus the640x360 thumbnail.
The thumbnail is an actual convolution-motion frame containing the complete CNN
and its orange receptive-field connection. It is not an unrendered concept image.

Actual checks in review-verification.json:

- Native types and counts match the model:1,4,4,8,8 feature planes; ten native dense
  nodes;392flattened activations; ten output probabilities. All eight stages stay
  in fixed positions throughout. Shapes and operation settings remain above them.
- Physical plane sides are2.856,2.856,1.428,1.428,0.714 units. Each pool halves the
  preceding spatial side while retaining the same channel count.
- Independently derived input/output window centers and sizes match recorded
  native geometry within1.78e-15 units. Convolution uses stride1,padding1; pooling
  uses stride2 and matching channels. Conv2 spans all four incoming planes.
- Every live response matches its saved tensor entry exactly. Origin-frame values
  were also inspected:0.2259 for Conv1/Pool1,0.0000 for Conv2,0.0020 for Pool2.
  Motion samples show changing coordinates and responses, e.g. Conv1(19,11)=0.2322
  and Pool2(4,5)=0.9594, consistent with the trace after rounding.
- At eight motion samples, a visible orange border is found exactly at projected
  input/output field corner pixels (0-pixel nearest distance). Native 3D lighting
  affects intensity, so this check uses hue and geometric distance, not flat RGB.
- Dense winner-node channel discrepancy is0.8/255. Softmax bar widths match the
  true probabilities subject only to a subpixel minimum for near-zero bars.
- Complete media decode, codec/dimensions/fps/file size, pure black corners and
  projected camera bounds passed. Header bitmap variation is3.21%, attributable
  to codec edge changes; layer positions and label content are fixed.

## Explanatory and typography assessment

The full native CNN is the primary visual throughout, matching the reference's
upright plane language and moving receptive-field connections. A first-filter
scan establishes convolution; remaining filter planes are highlighted in turn.
Pooling's one-channel connections are visibly different from Conv2's four-channel
volume. Smaller native planes communicate downsampling. A populated value vector,
fan-in signals, ten native dense nodes and output bars complete the forward pass.
Metrics and live scalar responses support the architecture without replacing it
with derivations. Prediction, sample cross-entropy and test accuracy are distinct.

Inspected initial/final holds and motion at960px/frame. Labels have safe projected
margins, the native nodes remain visible, captions fade sequentially, and compact
annotations remain above playback buttons. Mathematical labels/values use LaTeX
including native MathTex/Integer/DecimalNumber glyphs; prose is Liberation Sans.
Native LaTeX/font preflight passed. Black video and white website are retained.

Website integration is checked after approved local publication and before commit
and deployment. Results are recorded in website-verification.json.

## Website and repository checks

Strict Sphinx/Furo build and published-artifact integrity check passed. All27
repository tests passed against the combined cleanup and native CNN revision.
Browser QA played the actual new MP4 and waited for playback progress and settled
seeking. The Furo article contains the revised short explanation. Desktop player
remains736x414 and mobile358x201.375 before/during playback, with no media/page
errors or horizontal overflow. White background and Arial/Helvetica prose remain.
The CNN card exists and the redundant old forward-pass card is absent. Native
nodownload controls remain; no download links appear. Inspected the updated
review-website.png with the full native network and final metrics.

```sh
python3 scripts/website.py build
.venv/website/bin/python -m unittest discover -s tests
.venv/website/bin/python scripts/visualization_workflow.py check
.venv/website/bin/python tasks/mnist-cnn/check_website.py
```
