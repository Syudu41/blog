---
title: Four pixels, four predictions
description: See a 4–4–4 network recognize a tiny pattern, then learn through backpropagation.
alt: A black-background network connects four grayscale pixels to four ReLU neurons and four named pattern probabilities, with numerical weight matrices and an SGD update.
task: pixel-pattern-mlp
order: 60
media: assets/pixel-pattern-mlp/visualization.mp4
thumbnail: assets/pixel-pattern-mlp/thumbnail.png
width: 1920
height: 1080
---

A tiny grayscale image becomes four pixel intensities. The network's job is to choose **Vertical, Horizontal, Diagonal, or Anti-diagonal**. Think of four small lights: their brightness makes a pattern, and the network learns which name fits it. The calculations below follow the exact example in the video; displayed numbers are rounded.

**1. Turn the picture into numbers.** A pixel value of $0$ means black and $1$ means white. Reading left to right, top row first, gives:

$$
I=\begin{bmatrix}0.1&0.9\\0.1&0.9\end{bmatrix},
\qquad
x=\begin{bmatrix}0.1\\0.9\\0.1\\0.9\end{bmatrix}.
$$

Both right-hand pixels are bright, so the correct label is **Vertical**. The other labels represent a bright bottom row, a bright top-left/bottom-right diagonal, and the opposite diagonal. The architecture has $4$ input neurons, $4$ hidden neurons, and $4$ class outputs.

**2. Each hidden neuron mixes the inputs.** A weight acts like a volume knob: it controls how much a pixel adds or subtracts. A bias supplies an extra offset. For the first hidden neuron, multiply each pixel by its incoming weight, then add the bias:

$$
\begin{aligned}
z_1&=\sum_{i=1}^{4}w_{1i}x_i+b_1\\
&\approx (0.18283)(0.1)-(0.62399)(0.9)\\
&\quad +(0.45027)(0.1)+(0.56434)(0.9)\\
&\quad +0.2\\
&\approx 0.2096.
\end{aligned}
$$

ReLU is a simple gate: keep a positive result, replace a negative result with $0$.

$$
h_1=\max(0,0.2096)=0.2096.
$$

The second neuron gets $z_2\approx-0.7833$, so its output is $h_2=0$. Applying the same rule to all four neurons gives:

$$
h\approx(0.2096,\;0,\;0.2111,\;0.3767)^{\mathsf T}.
$$

**3. Turn hidden values into class probabilities.** The output layer mixes these hidden values with a second set of weights. Its four raw scores, called *logits*, are:

$$
\begin{aligned}
\ell&=W^{(2)}h+b^{(2)}\\
&\approx(0.1220,\;0.0806,\;0.0801,\;0.1928)^{\mathsf T}.
\end{aligned}
$$

Softmax turns those scores into positive shares that add to $1$. For Vertical, the calculation is:

$$
\begin{aligned}
S&=e^{0.1220}+e^{0.0806}+e^{0.0801}+e^{0.1928},\\
p_{\mathrm{Vertical}}&=\frac{e^{\ell_1}}{\sum_{j=1}^{4}e^{\ell_j}}
\approx\frac{e^{0.1220}}{S}\approx0.2505.
\end{aligned}
$$

In the label order above, the network assigns approximately $25.05\%$, $24.04\%$, $24.02\%$, and $26.89\%$. Anti-diagonal initially gets the largest share, so this first guess is wrong.

**4. Measure the mistake.** The training label tells the network that Vertical is correct. Cross-entropy asks how little probability it gave that correct answer:

$$
\mathcal L=-\ln p_{\mathrm{Vertical}}
\approx-\ln(0.25051)\approx1.3843.
$$

Giving Vertical more probability makes this loss smaller. Loss is a score computed after the prediction; it is not another neuron input.

**5. Trace the mistake backward and adjust a weight.** Backpropagation calculates how each weight affects the loss. At the output, the error signal is the probability vector minus the correct one-hot label:

$$
\begin{aligned}
y&=(1,0,0,0)^{\mathsf T},\\
\delta^{(2)}&=p-y\\
&\approx(-0.7495,\;0.2404,\;0.2402,\;0.2689)^{\mathsf T}.
\end{aligned}
$$

The hidden layer receives that error through the output weights. ReLU blocks it wherever the earlier weighted sum was negative:

$$
\delta^{(1)}=
\bigl((W^{(2)})^{\mathsf T}\delta^{(2)}\bigr)
\odot\mathbf1_{z>0}.
$$

Here $\odot$ means multiply matching entries, and $\mathbf1_{z>0}$ is $1$ for an open ReLU gate and $0$ for a closed one. For the highlighted edge from $x_2$ to $h_1$, this gives:

$$
\begin{aligned}
\frac{\partial\mathcal L}{\partial W^{(1)}_{1,2}}
&=\delta^{(1)}_1x_2\\
&\approx(-0.1563646)(0.9)\\
&\approx-0.1407281.
\end{aligned}
$$

A gradient is a direction hint. This negative value says that increasing this weight slightly should reduce the loss. SGD follows that hint with a step size of $\eta=0.08$:

$$
\begin{aligned}
w_{\mathrm{new}}&=w_{\mathrm{old}}-\eta\frac{\partial\mathcal L}{\partial w}\\
&\approx-0.623990-0.08(-0.140728)\\
&\approx-0.612732.
\end{aligned}
$$

All $40$ parameters (weights and biases) use gradients computed from the old network in this same update. A closed ReLU can give some parameters a zero gradient.

**6. Try the same picture again.** After just that update, Vertical's probability rises from about $25.05\%$ to $27.24\%$, and its loss falls from $1.3843$ to $1.3005$. The pixels have stayed the same; the learned parameters changed.

The video then shows recorded training checkpoints. After $2048$ SGD updates, this image receives about $99.36\%$ probability for Vertical, with loss $0.0064$. The experiment uses $128$ training images and $64$ separate test images; the final network classifies $64/64$ test images correctly. These results describe this small synthetic pattern task.
