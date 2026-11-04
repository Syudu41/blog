# Original TensorQuill CNN showcase

Original Manim animation with perspective feature-map stacks, detailed cells, continuous eased window motion, coordinated dense-layer pulses, stable composition, and no cartoon. Inspired by ManimML’s CNN showcase, without copying its asset.

Visualize a deterministic valid stride-one CNN: 1x7x7 input, 3x5x5 ReLU features, 4x3x3 ReLU features, flatten to 36, dense 5, softmax 3. Reveal each output spatial location as its receptive field is scanned. Activation fills and output scores must match actual computed values.

White background, Arial-family prose, LaTeX for dimensions and formulas, readable at README width 900; no overlapping labels or clipped objects. GIF loops, 1200x600 near 30fps, under12MB, with PNG thumbnail.

## Storyboard

Establish the complete architecture with faint cells and edges. Highlight the input. Scan a receptive field continuously in a serpentine traversal, revealing three first-layer feature maps one spatial location at a time. Pass three-channel receptive fields through the next convolution and reveal four smaller maps. Send computed values through the dense connections and show the softmax prediction. Hold the completed network, then gently reset for the repeat.

Quality reference: https://github.com/helblazer811/ManimML/blob/5e8f7cb69f23919f9ec7e880fb22c1ca2f841c08/Readme.md . This is an original scene and computed example; no upstream media is embedded. Review window travel, reveal timing, stack depth, dense pulses, final-size legibility, and the reset. The loop illustrates the mechanism, without claiming to teach all of CNN training.
