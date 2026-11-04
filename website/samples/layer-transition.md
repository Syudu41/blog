---
title: A forward pass through a neural network
description: Follow a forward pass from three inputs through four hidden neurons to two outputs.
task: layer-transition
media: assets/layer-transition/visualization.mp4
thumbnail: assets/layer-transition/thumbnail.png
alt: A three-input, four-hidden-neuron, two-output network; orange signals travel left to right and blue fills show computed activations.
order: 30
width: 1920
height: 1080
---

Watch three inputs pass through four hidden neurons to two outputs. Orange pulses mark information moving along connections; blue intensity shows each neuron’s activation. A layer receives its signals before its values appear.

This example uses fixed illustrative weights: the hidden layer computes $h=\operatorname{ReLU}(W_1x+b_1)$, and the output layer computes $y=\sigma(W_2h+b_2)$. The two outputs are independent sigmoid values, rather than a softmax probability distribution. Values inside nodes are rounded to two decimal places. This is a forward-pass demonstration, not a trained classifier.
