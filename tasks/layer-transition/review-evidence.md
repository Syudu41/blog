# Forward-pass example review

The storyboard establishes the architecture, inputs, hidden computation, output computation, and completed pass. This short animation illustrates the causal sequence. Its surrounding page defines ReLU and sigmoid operations; it does not attempt a training or backpropagation lesson.

Inspected the actual final MP4 through ten extracted frames in `review-stages-1.png`, `review-stages-2.png`, and `review-stages-3.png`, including two times during each signal transition. Also inspected the final 640×360 thumbnail. The input, hidden and output layers remain fixed, orange dots and passing flashes move along the edges, and hidden/output values appear only after signals arrive. Blue fill shows activation strength on the same intensity scale across all layers. The sequence ends with a readable completed hold and a gentle reset. All labels fit without collision; the draft's lowest-hidden-neuron collision was fixed before the final render. Numbers remain readable at the reviewed 900-pixel display size. The thumbnail is derived from the completed hold, rather than a fading reset frame.

The scene uses actual ManimML FeedForwardLayer and NeuralNetwork objects, with 3, 4, and 2 nodes, and 12 plus 8 connections. Custom Manim pulse timing makes each phase explicit. Caption changes crossfade while the architecture stays in place. The draft and final were rendered separately using the TensorQuill CLI.

`checks.py` independently recomputes the hidden layer and sigmoid outputs using Python math.fsum and math.exp. Hidden values are [0.675,0.36,0.68,0.39]; outputs are [0.6938116308,0.5732197727]. The scene displays them rounded to two decimals. These are independent sigmoid outputs with fixed illustrative weights, as the page explains. Pixel samples in each node at five stages independently verify the causal activation sequence and activation colors; maximum color-channel error is 1.84/255 after encoding. Recorded geometry verifies node counts, edge counts, and label clearance.

Every MP4 frame was decoded: 427 frames, 1920×1080, H.264/yuv420p, 30fps, 14.233 seconds, 1,913,595 bytes. First-to-last mean channel difference is 0.0056/255. Thumbnail PNG integrity passed at 640×360. `verification.json` records measurements, SHA-256, stage times, and actual tool versions; `computation.json` records every input, weight, bias and activation.

All node numbers are MathTex rendered with LaTeX. Prose uses installed Liberation Sans, an Arial-compatible font. Native LaTeX smoke test passed.

Final command: `TENSORQUILL_TEX_BIN=/home/lab335a/Sudarshan/Research-PhD/visualizer/.venv/tex/bin/x86_64-linux python3 -m tensorquill render tasks/layer-transition --python .venv/render/bin/python --preset final` (exit0). Verification: `.venv/render/bin/python tasks/layer-transition/checks.py` (exit0).

Website integration: all24 repository tests passed; strict Sphinx dirhtml build passed. Headless Chrome played the built video on desktop and mobile with no media errors or horizontal overflow. Size stayed736×414 before/during desktop playback and358×201.375 on mobile. Inspected review-website.png; see website-verification.json for actual bounds.
