# README animation review

Purpose: communicate that TensorQuill is under construction through a sculptor metaphor. This is not a numerical neural-network explanation.

Progression: establish a labeled 2–3–1 network with three rough hidden-layer stones; swing the hammer against a chisel; shape each stone into a node in turn; hold the finished layer; return to the starting pose for the loop.

Reviewed the actual final GIF using six recorded stage frames in `review-stages.png`, the strike sequence in `review-motion.png`, and the 640-pixel thumbnail. The sculptor, hammer, chisel, rough stones, and finished nodes remain recognizable. Labels stay fixed and clear, all elements fit the white canvas, and the reset restores the initial rough layer. Edges behind the sculptor are intentional background context. The action reveals construction rather than computed activation.

`checks.py` decoded every frame, verified dimensions, infinite looping, duration, frame rate, file size, PNG integrity, and near-identical reset pose. See `verification.json` for measurements and the actual rendering environment. Rerun after rendering with `.venv/render/bin/python tasks/readme-wip/checks.py`.

No equations or numerical values are presented. The topology has two inputs, three hidden nodes, one output, and nine connections. Prose uses Liberation Sans, an Arial-compatible font. The renderer also passed its LaTeX environment smoke test.
