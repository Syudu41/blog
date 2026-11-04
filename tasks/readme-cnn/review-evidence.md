# Original CNN showcase review

## Reference and scope

Inspected the actual ManimML README CNN GIF (1900×700, 500 frames), including its spatial feature-map stacks, sliding receptive fields, connectors, and dense pass. Also inspected the official Manim OpeningManim demonstration frames and transition code. The new TensorQuill scene implements its own computation and projected cell geometry. No upstream media is included.

This README showcase establishes a spatial computation sequence; it is not a complete CNN lesson or a trained recognition model. Fixed illustrative weights are identified in the animation. The website gallery is unchanged.

## Final visual inspection

Inspected `review-stages-1.png`, `review-stages-2.png`, `review-motion.png`, `review-flow.png`, and the actual PNG thumbnail. Stage frames come from the final GIF at the recorded times, displayed at the intended 900-pixel README width. The input, three first-stage maps, four second-stage maps, dense nodes, and three outputs remain fixed throughout. Projection and occlusion preserve the feature-map stack order. Labels, dimensions, and caption have clear separation and fit the canvas.

The motion sequence at 1.83–2.13 seconds shows the receptive field moving continuously across cells, with matching feature reveals and connected orange guides. The second scan covers the next feature stack. Flow frames at 9.10, 9.50, 10.95, and 11.35 seconds show particles traveling from map rows to dense nodes and from dense nodes to outputs. The final prediction displays 0.46, 0.27, 0.28, consistent with rounded computed probabilities, and outlines the largest. The final hold is followed by a fade back to the starting geometry. Residual pulse dots seen in the draft were removed in the final source and are absent in the reviewed reset frame.

The two convolution stages scan all 25 and 9 spatial positions respectively. Colors encode normalized activation intensity within each layer; they are not raw probability values. Map-to-dense connections bundle each row for readability, as explained in `content.md`. Dense output connection thickness reflects absolute weight. Orange indicates the active operation or moving signal; the output ring identifies the maximum probability. This is a schematic rendering of a real deterministic tensor computation, not a literal physical neural network.

## Automated evidence

`checks.py` independently recomputes both valid stride-one convolutions with explicit loops, then dense activations and softmax. Maximum numerical discrepancy is below 5e-16. It also compares every visible front-map cell's final color against the computed activation; maximum channel discrepancy is 9.68/255 after GIF quantization and compression.

Every GIF frame was decoded: 460 frames, 1200×600, 15.33 seconds, average 30.0065 fps, infinite loop, 9,101,762 bytes. First-to-last mean channel difference is 0.660/255. The PNG thumbnail verifies at 640×320. Measurements, SHA-256, stage times, and actual rendering tool versions are in `verification.json`; the full computed tensors and weights are in `computation.json`.

Final command: `TENSORQUILL_TEX_BIN=/home/lab335a/Sudarshan/Research-PhD/visualizer/.venv/tex/bin/x86_64-linux python3 -m tensorquill render tasks/readme-cnn --python .venv/render/bin/python --preset final` (exit 0). Verification: `.venv/render/bin/python tasks/readme-cnn/checks.py` (exit 0). Prose uses installed Liberation Sans; dimensions and probabilities use MathTex/LaTeX, with successful native LaTeX smoke test.
