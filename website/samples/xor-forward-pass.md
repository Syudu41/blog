# XOR: inside a forward pass

<video controls controlslist="nodownload" playsinline preload="metadata" width="1920" height="1080" style="aspect-ratio: 1920 / 1080;" poster="../assets/xor-forward-pass/thumbnail.png" aria-label="A 2-2-1 XOR network with activation-function graphs above the neurons. The input (1,0) produces hidden values (1,0), output logit5 and prediction0.9933."><source src="../assets/xor-forward-pass/visualization.mp4" type="video/mp4">A 2-2-1 XOR network with activation-function graphs above the neurons. The input (1,0) produces hidden values (1,0), output logit5 and prediction0.9933.</video>

One forward pass solves the XOR input $x=(1,0)$ with target $y=1$. Markers on the graphs show how each weighted sum becomes an activation: $h_1=\operatorname{ReLU}(x_1-x_2)=1$ and $h_2=\operatorname{ReLU}(x_2-x_1)=0$. Those values travel to the output, where $z=10h_1+10h_2-5=5$ and $\hat y=\sigma(z)\approx0.9933$. The threshold $0.5$ gives the predicted class $1$.

The weights are chosen for clarity, rather than learned during the animation. The hidden layer uses $W_1=\begin{bmatrix}1&-1\\-1&1\end{bmatrix}$ and $b_1=(0,0)$; the output uses $W_2=\begin{bmatrix}10&10\end{bmatrix}$ and $b_2=-5$. Binary cross-entropy is computed **after** the prediction: $\mathcal L=-y\ln\hat y-(1-y)\ln(1-\hat y)\approx0.006715$. It does not feed into the forward pass.

| Input | Target | Prediction |
| --- | --- | --- |
| $(0,0)$ | $0$ | $0.0067$ |
| $(0,1)$ | $1$ | $0.9933$ |
| $(1,0)$ | $1$ | $0.9933$ |
| $(1,1)$ | $0$ | $0.0067$ |

The video follows only $(1,0)$. All four cases are checked to verify that the chosen network implements XOR. The visual style draws inspiration from [ManimML’s animated logo](https://github.com/helblazer811/ManimML).

[Back to sample visualizations](index.md)
