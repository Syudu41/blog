# Why cross-entropy penalizes confident mistakes

*Sample post · Sudarshan Balaji · 8 November 2026*

A model can make a wrong prediction while barely preferring one answer, or it can be almost certain about the wrong answer. Cross-entropy gives the second mistake a larger penalty. Here is a small example of why.

## Start with the correct answer

Suppose an image contains a vertical pattern. Let $p$ be the probability that the model assigns to **Vertical**, the correct label. For a single example with one correct class, cross-entropy is:

$$
\mathcal L=-\ln p.
$$

The logarithm here is the natural logarithm. Loss gets smaller as the model gives the correct answer more probability.

## Put numbers into the formula

| Probability assigned to the correct label | Calculation | Loss, rounded |
| --- | --- | --- |
| $0.90$ | $-\ln(0.90)$ | $0.1054$ |
| $0.50$ | $-\ln(0.50)$ | $0.6931$ |
| $0.01$ | $-\ln(0.01)$ | $4.6052$ |

For a concrete confident mistake, imagine the model assigns $99\%$ to **Horizontal**, the wrong label, and $1\%$ to **Vertical**. Its loss is approximately $4.6052$. If it instead assigns $90\%$ to Vertical, its loss is only about $0.1054$.

The important quantity is the probability of the correct answer, rather than just whether the largest probability belongs to the correct label.

## Check it with Python

```python
import math

for probability in (0.90, 0.50, 0.01):
    loss = -math.log(probability)
    print(f"p={probability:.2f}, loss={loss:.4f}")
```

Output:

```text
p=0.90, loss=0.1054
p=0.50, loss=0.6931
p=0.01, loss=4.6052
```

These examples use positive probabilities. As $p$ approaches $0$, the loss grows without bound; at $p=1$, the loss is $0$.

## Connect the number to learning

Backpropagation calculates how the model's parameters affect this loss. An optimizer then uses those gradients to adjust the parameters. Smaller loss on one training example means that the model assigned that example's correct class more probability; evaluating separate test examples helps us assess what it learned beyond that example.

The [four-pixel neural-network visualization](../samples/pixel-pattern-mlp.md) shows this process with actual weights, predictions, and a gradient update. In its first update, the correct class probability rises from approximately $0.2505$ to $0.2724$, while cross-entropy falls from $1.3843$ to $1.3005$.
