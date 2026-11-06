# Four pixels, four predictions

Classify a synthetic 2x2 grayscale image as Vertical, Horizontal, Diagonal or Anti-diagonal. Define row-major input pixel order and class prototypes visually; identify probabilities as softmax outputs, not pixel intensities. Clearly label the toy task.

Use a persistent native ManimML 4-input, 4-ReLU-hidden, 4-softmax-output network on black. Keep the actual pixel image, meaningful class glyphs and probability bars visible. Motion follows pixels to inputs, weighted sums to hidden activations, logits to probabilities.

Show both full numerical 4x4 weight matrices above the corresponding connection groups, row i as the incoming weight vector of neuron i. Match a highlighted row to its incoming edges. Signed edge color represents weight sign; width represents magnitude. Include both bias vectors. First-layer weights can be reshaped spatially; output weights cannot.

Show actual float64 first forward pass, cross-entropy against Vertical target, backpropagation through softmax and ReLU, one selected scalar gradient and simultaneous SGD update with learning rate 0.08. Replay the same image after that update, then actual saved training checkpoints through update 2048. Plot same-image loss and show held-out toy test counts. Distinguish gradients, weights and activations.

User override: Computer Modern Roman prose via LaTeX Tex; all math via MathTex. White CMR text on black with teal, pink and amber accents. No Pango prose in the video. Explain what is predicted, what the inputs represent, and what the outputs mean.

Network remains primary; supporting equations occupy a separate lower band. Smooth causal signals, stable object identities, focused highlights, readable complete numerical matrices, generous holds. Inspect actual transitions and final output, 1920x1080 30fps H264 video with a useful thumbnail. All displayed numbers must agree with trace.json and independent checks.

## Storyboard

1. Show the actual 2x2 image and four named prototype glyphs. Ask which pattern the image contains. Define grayscale range and row-major pixel order, then move copies of those exact pixels into four input neurons.
2. Keep the entire 4–4–4 network central. Reveal W1 and W2 above their connection groups, biases below, and a signed-weight legend. Focus W1 row1 and its incoming connections. Send actual input values along edges; evaluate its dot product and ReLU. Commit all four hidden values, including the clipped negative preactivation.
3. Focus W2 row1 and its incoming hidden connections. Transmit hidden activations, evaluate logits, then reveal softmax probabilities beside named class glyphs. Initially Anti-diagonal narrowly leads; the true target is Vertical.
4. Cross-entropy is computed after the output. Backward pulses follow the output-to-hidden-to-input direction. Explain delta=p-y and the ReLU gate. Inspect one incoming weight derivative, then update all weights and biases simultaneously.
5. Replay the same input after update1, updating the actual matrices, edge encodings, nodes and probability bars. Show the increased target probability and reduced loss.
6. Show recorded checkpoints32,128,512,1024,2048 with a growing same-image loss curve and separately labeled held-out correct counts. No interpolated curve points are claimed as recorded observations. End with the final live network, readable weights and class probabilities.

## Reference and limitations

User reference: https://www.youtube.com/watch?v=LEAFHHNk8II (Computational Thinking, Convolutional Neural Networks). Public max-resolution thumbnail inspected: black canvas, Computer Modern numerals, teal/pink signed numerical emphasis. Full playback and yt-dlp were blocked by YouTube traffic/sign-in checks, so no claim of matching its timing or unseen sequences. The source reference concerns convolution; this requested example is explicitly a dense MLP, with no convolutional filters.

This is a synthetic toy classification problem, not MNIST or a natural-image benchmark. Bright/dark prototypes are perturbed with independent Gaussian noise (sigma0.13), clipped to[0,1].128 training and64 separate test examples. SGD uses one example per update, fixed learning rate0.08. The demonstrated first update uses the explicitly named example; subsequent examples are shuffled training data. Rounded labels are display values; training uses float64. The test score is an illustrative held-out toy score. CMR is the explicit user-selected font for this video; the website retains its existing Arial-family text.
