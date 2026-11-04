# Input → hidden → output

<video controls controlslist="nodownload" playsinline preload="metadata" width="1920" height="1080" style="aspect-ratio: 1920 / 1080;" poster="../assets/layer-transition/thumbnail.png" aria-label="A three-input, four-hidden-neuron, two-output network; orange signals travel left to right and blue fills show computed activations."><source src="../assets/layer-transition/visualization.mp4" type="video/mp4">A three-input, four-hidden-neuron, two-output network; orange signals travel left to right and blue fills show computed activations.</video>

Watch three inputs pass through four hidden neurons to two outputs. Orange pulses mark information moving along connections; blue intensity shows each neuron’s activation. A layer receives its signals before its values appear.

This example uses fixed illustrative weights: the hidden layer computes $h=\operatorname{ReLU}(W_1x+b_1)$, and the output layer computes $y=\sigma(W_2h+b_2)$. The two outputs are independent sigmoid values, rather than a softmax probability distribution. Values inside nodes are rounded to two decimal places. This is a forward-pass demonstration, not a trained classifier.

[Back to sample visualizations](index.md)
