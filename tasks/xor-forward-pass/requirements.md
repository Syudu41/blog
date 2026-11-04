# XOR: inside a forward pass

One forward pass for XOR input(1,0), target1, through a2-2-1 MLP using ManimML primitives. Chosen weights, no training or updates. Thin connections, outlined neurons, subtle layer frames and smooth causal highlights inspired by the ManimML logo.

Show ReLU graphs above both hidden neurons and sigmoid above the output. Explicitly trace weighted sums1 and-1 through ReLU to1 and0; carry these activations along output connections; show output logit5 passing through sigmoid to0.9933. Activation graphs are not loss graphs.

Use W1=[[1,-1],[-1,1]],b1=[0,0],W2=[[10,10]],b2=-5. Verify all four XOR cases independently. Show threshold0.5, predicted1, target1 and BCE about0.006715 after the output. Do not feed loss into a neuron.

White canvas, Arial-family prose, all mathematical labels and numbers in LaTeX. Stable architecture and readable nonoverlapping graph labels, equations and captions. Deliver1080p30fps H264 video and a useful PNG thumbnail. Review actual transitions and graphical mappings.

## Storyboard

Establish the2-2-1 architecture, graph annotations and the selected input/target. Activate the inputs. Send weighted signals into the hidden layer and display both weighted sums. Focus on each hidden neuron in turn: move a marker to the input on the graph’s horizontal axis, project to the ReLU curve, then to its output on the vertical axis. Reveal the corresponding neuron value. Send hidden activations to the output. Form logit5, trace the sigmoid graph and reveal prediction0.9933. Compare with target1, classify at0.5, show the small BCE loss, and hold the finished state.

The graphs annotate activation functions, not the loss. Loss is evaluated after prediction. No training, weight changes or repeated input examples are animated. The hidden negative preactivation must visibly map to zero. Surrounding page defines all weights and the XOR table.

Reference inspected: ManimMLLogo.gif from https://github.com/helblazer811/ManimML . Preserve its sparse outlined-network treatment and travelling highlights, adapted to the required white background. Original media only.
