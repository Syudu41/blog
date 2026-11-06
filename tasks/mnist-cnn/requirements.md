# MNIST CNN: ManimML layer and receptive-field representation

The user rejected the mathematical slide layout and the subsequent tilted raster
thumbnail stacks. The requested reference is ManimML's actual CNN showcase.
Use its native vector Convolutional2DLayer, MaxPooling2DLayer, FeedForwardLayer
and Filters objects: upright translucent channel planes, moving gridded input
windows, and orange connective volumes ending at corresponding output locations.
The complete CNN must be the dominant, persistent visual, with readable shapes,
settings and measured metrics above it. Black video background; short page prose.

## Mathematical contract

Keep the immutable trained trace (trace.npz SHA256
10495cd69b1ec51a77e20a38549296fb491e8bf72467f4af261e659e613f5f11).
MNIST test index0,target7,pixels/255. The original training split is0:55000,
validation55000:60000,test10000images. Seed2026,Adam learning rate0.001,
batch128,four epochs; all weights are frozen during this inference animation.

Architecture, channels/height/width with batch omitted:

- Input1x28x28.
- Conv1+ReLU:4filters,3x3,stride1,zero padding1;4x28x28,40parameters.
- Pool1:2x2,stride2,per channel;4x14x14,0parameters.
- Conv2+ReLU:8filters spanning all4incoming channels,3x3,stride1,padding1;
  8x14x14,296parameters.
- Pool2:2x2,stride2,per channel;8x7x7,0parameters.
- Flatten392values,0parameters; preserve channel/row/column order.
- Dense392to10logits,3930parameters including biases.
- Softmax10probabilities,0learned parameters.

Use cross-correlation, not a flipped mathematical convolution. The live coordinate
and activation readout must come from the saved trace. Convolution input windows
start at output index minus one for padding; pooling windows start at twice the
output index. A second-convolution filter spans all four source planes; a pooling
window maps one source plane to the matching output plane, never across channels.
Record actual runtime window centers/corners and values for independent checks.

Blue translucent planes communicate layer/channel geometry and processing state;
they do not claim a synthetic per-pixel activation heatmap. Input grayscale comes
from the real image; flattening retains all392actual activations; the ten output
bars use actual probabilities. Layer maxima, selected responses, parameter counts,
class, cross-entropy and full-test accuracy must be independently verified.
Keep sample confidence/loss distinct from dataset accuracy.

## Storyboard and visual review

1. Start with all eight stages and an actual grayscale digit on the native input
   plane. Define orange receptive fields and coupled output locations.
2. Focus Conv1: hold an initial padded window with its correct numeric response,
   then smoothly scan the native input-to-output filter volume across one channel.
   Highlight the remaining output channels to generalize to all four filters.
3. Focus Pool1: move a2x2window to its matching output pixel, showing per-channel
   spatial reduction and the actual response. Keep all four channel planes.
4. Focus Conv2: the orange volume spans all four incoming planes and reaches one
   of eight output planes. Scan one filter, then highlight the remaining filters.
5. Focus Pool2: reduce spatial dimensions independently, retaining eight channels.
6. Unfold the392pooled activations into a vector; send signals along fan-in lines
   to ten native dense neurons; highlight the winning score.
7. Grow the actual softmax bars. Hold the entire CNN with prediction confidence,
   cross-entropy and test accuracy below it; retain all layer shapes/settings above.

Keep the full architecture in fixed positions throughout; remove the separate
thumbnail-gallery strips and full-screen derivations. Use stable camera framing,
spaced upright vector planes, native receptive-field connections and smooth
transitions. Inspect native layer visibility, padding/stride/channel geometry,
readout updates, initial/final holds and actual motion frames. All math uses
LaTeX, prose Liberation Sans. Validate projected camera bounds, not only3D source
bounds. Captions must clear native playback buttons. Deliver1080p30H264/yuv420p
MP4 under30MB and a full-network thumbnail; re-review before website publication.

## Inspected references

- ManimML CNN GIF: https://github.com/helblazer811/ManimML/blob/main/assets/readme/convolutional_neural_network.gif
- Image-fed CNN: https://github.com/helblazer811/ManimML/blob/main/assets/readme/convolutional_neural_network_with_an_image.gif
- Native primitives: https://github.com/helblazer811/ManimML#convolutional-neural-networks
- Focus/causal pacing: https://www.3blue1brown.com/lessons/neural-networks/
  (this digit example is fully connected; the present task is a CNN).
- Review rubric: ../../docs/visual-standards.md.
