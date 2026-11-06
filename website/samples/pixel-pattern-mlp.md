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

A tiny grayscale image becomes four pixel intensities. A 4–4–4 network predicts **Vertical, Horizontal, Diagonal, or Anti-diagonal**; the bars show class probabilities. Follow the visible weight vectors through one forward pass, cross-entropy loss, and a real backpropagation update, then watch the same image improve during training. This is a synthetic toy problem, with 128 training images and 64 separate test images.
