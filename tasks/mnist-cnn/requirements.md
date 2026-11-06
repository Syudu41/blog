# MNIST: inside a convolutional network

Audience: technical and ML viewers. Requested: a polished CNN animation on a black
video background, with correct numbers and a short website description.

## Mathematical contract

Real MNIST test image at fixed index 0. Normalize pixels by 255. Train on original
training indices 0:55000, validate on 55000:60000, and evaluate once on the original
10000-image test split. Fixed seed 2026, four epochs of Adam, learning rate 0.001,
batch size 128. No training or weight update is depicted in this inference video.

Architecture (channel, height, width; batch omitted):
1x28x28 -> Conv(1,4,3,padding=1,stride=1) -> ReLU -> 4x28x28 ->
MaxPool(2,stride=2) -> 4x14x14 -> Conv(4,8,3,padding=1,stride=1) -> ReLU ->
8x14x14 -> MaxPool(2,stride=2) -> 8x7x7 -> flatten 392 -> linear 10 -> softmax.
Convolutions use cross-correlation, the framework convention; kernels are not
flipped. The second convolution sums over all four input channels. Cross-entropy
is computed from logits; softmax is displayed to explain predictions.

All feature maps, example kernel/patch values, pooled values, logits, probabilities
and loss must come from trace.npz. Record the trained model, provenance, split,
metrics and hashes. No invented metrics or illustrative replacement features.
Use a shared zero-to-layer-maximum display scale across each post-ReLU layer;
disclose that heatmap brightness is normalized for display. Input remains grayscale.

## Storyboard and visual progression

1. Establish the question with a large real handwritten image, input dimensions,
   normalization and target. Let viewers inspect the image.
2. Focus on one actual receptive field. Enlarge the normalized patch and one
   learned kernel. Reveal their elementwise products, sum and bias, then ReLU.
3. Return to the image and build one computed activation map with a moving
   receptive field and corresponding output position. Show zero padding and
   shared weights, then extend from one channel to all four actual feature maps.
4. Show one 2x2 activation window and its exact maximum. Animate spatial
   reduction and reveal all four pooled maps, preserving channel identity.
5. Show the second convolution's four-channel sum and eight computed maps,
   then the second pooling and flattening into 392 features.
6. Connect features to ten logits, then probability bars, class, target, sample
   cross-entropy and measured test accuracy. End on a clean readable hold.

Use stable positions within each explanation, smooth transforms and purposeful
highlights. One expanded numerical operation at a time. No graphs over neurons,
no decorative signal that claims a numerical result. Use cyan for activations,
amber for the selected receptive field, and violet for the second convolution.
All math including dimensions/numerical labels uses LaTeX; prose uses Liberation
Sans (Arial family). Pure black background, high contrast, safe frame margins.
Render a draft for inspection, then final 1920x1080 at 30 fps, H264/yuv420p, useful
thumbnail, under 30 MB. Review holds and transitions at 960px width and the built
website. Publish only after numerical, media, typography and visual checks pass.

## References

- Visual pacing reference: https://www.3blue1brown.com/lessons/neural-networks/
  (its digit classifier is fully connected; this task is an actual CNN).
- Dataset: https://www.tensorflow.org/datasets/catalog/mnist
- Computation: https://docs.pytorch.org/docs/2.5/generated/torch.nn.Conv2d.html
- Local explanatory rubric: ../../docs/visual-standards.md
