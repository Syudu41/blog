# XOR activation-graph review

## Scope and visual reference

One forward pass uses input(1,0) and target1. There is no training or weight change. The graphs are activation functions: ReLU above both hidden neurons, sigmoid above the output. The loss is a small result after prediction. Inspected ManimMLLogo.gif itself (1920×500,1000frames) for its outlined nodes, thin connections, layer frames and travelling highlights. This original scene uses ManimML FeedForwardLayer/NeuralNetwork primitives with the required white background.

## Actual final inspection

Inspected all18 sampled final frames across review-stages-1.png through review-stages-5.png, at900px per frame, and the640×360 final thumbnail. The input pair and target are explicit. Signals first form the weighted sums, then each hidden graph is evaluated separately. The orange graph outline and cursor identify the active operation. A marker travels from the input axis to the function and projects to the output axis. The positive ReLU maps1to1; the negative ReLU maps-1to0. Each graph result moves into its neuron before hidden signals are sent onwards. Early/late samples of both connection phases show continuous left-to-right movement.

The output sum is10(1)+10(0)-5=5. The sigmoid marker shows input5 and output0.9933, followed by the output-neuron value. Classification at0.5 yields1, matching the target. BCE0.006715 appears only afterwards, with no feedback arrow. The completed scene is held for3seconds. Activation-graph labels and results, phase captions, layer names and node values fit the canvas without clipping or label collisions. White graph annotation panels intentionally sit over the faint structural frame and background connections; the function-to-neuron arrows remain visible.

Each step retains object identity and the architecture. Input and output weights are explained by the equations and surrounding page; zero-valued pulses carry a zero value rather than encoding signal magnitude. Node fill intensity follows the actual activation value. This is a short graphical forward-pass demonstration, not a derivation of training or backpropagation.

## Numerical and media checks

checks.py independently verifies the exact weights, all4 XOR truth-table classifications, preactivations, ReLU values, logits, sigmoid probabilities, and stable BCE using math.log1p. Maximum arithmetic error1.25e-16. It verifies the2-2-1 node topology and4+2 connections, plus causal ordering from the stage timestamps.

Actual pixels independently confirm that the cursor sits on each function’s correct result (maximum sampled orange-channel error5/255) and that final node fills encode the computed activations (maximum channel error2.15/255).

Decoded every final video frame:1004frames,1920×1080,H264/yuv420p,30fps,33.467seconds,3,255,686bytes. PNG thumbnail verifies at640×360 and comes from the completed hold. SHA256, actual environment, measurements and stage times are in verification.json. Full weights and all4 computations are in computation.json; diagram and function-marker positions are in layout.json.

Prose uses installed Liberation Sans. All numbers, mathematical labels, equations and graph labels are MathTex/LaTeX. Native LaTeX smoke test passed. Numerical graph inputs/outputs are additionally visible in the larger phase equations.

Final command: TENSORQUILL_TEX_BIN=/home/lab335a/Sudarshan/Research-PhD/visualizer/.venv/tex/bin/x86_64-linux python3 -m tensorquill render tasks/xor-forward-pass --python .venv/render/bin/python --preset final (exit0,63animations). Verification: .venv/render/bin/python tasks/xor-forward-pass/checks.py (exit0).

Website verification: all24 tests and strict Sphinx build passed. Headless Chrome confirmed working video playback, stable736×414 desktop and358×201.375 mobile sizing, no horizontal overflow, hidden download controls and no MathJax errors. Inspected review-website.png, including the correctly rendered2-row weight matrix and XOR table. Measurements in website-verification.json.

Introduction re-review: preserved the user-authored paragraph added in f18e6ed. Its single-pass and layer-count claims match the video and task; inspected ReLU and final-prediction/motion frames, reran checks.py, and confirmed source/artifact hashes are unchanged. Archived the previous review and prepared a fresh complete review covering the new content. No rerender required because source and artifacts are unchanged.
