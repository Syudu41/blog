One forward pass solves the XOR input $x=(1,0)$ with target $y=1$. Markers on the graphs show how each weighted sum becomes an activation: $h_1=\operatorname{ReLU}(x_1-x_2)=1$ and $h_2=\operatorname{ReLU}(x_2-x_1)=0$. Those values travel to the output, where $z=10h_1+10h_2-5=5$ and $\hat y=\sigma(z)\approx0.9933$. The threshold $0.5$ gives the predicted class $1$.

The weights are chosen for clarity, rather than learned during the animation. The hidden layer uses $W_1=\begin{bmatrix}1&-1\\-1&1\end{bmatrix}$ and $b_1=(0,0)$; the output uses $W_2=\begin{bmatrix}10&10\end{bmatrix}$ and $b_2=-5$. Binary cross-entropy is computed **after** the prediction: $\mathcal L=-y\ln\hat y-(1-y)\ln(1-\hat y)\approx0.006715$. It does not feed into the forward pass.

| Input | Target | Prediction |
| --- | --- | --- |
| $(0,0)$ | $0$ | $0.0067$ |
| $(0,1)$ | $1$ | $0.9933$ |
| $(1,0)$ | $1$ | $0.9933$ |
| $(1,1)$ | $0$ | $0.0067$ |

The video follows only $(1,0)$. All four cases are checked to verify that the chosen network implements XOR. The visual style draws inspiration from [ManimML’s animated logo](https://github.com/helblazer811/ManimML).
