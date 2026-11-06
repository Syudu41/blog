"""Train the small CNN and export an immutable, framework-free inference trace.

Usage: .venv/render/bin/python tasks/mnist-cnn/train.py /tmp/tensorquill-mnist.npz
Training needs CPU torch==2.5.1; rendering only needs NumPy and Manim.
"""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import torch
from torch import nn

ROOT = Path(__file__).resolve().parent
SEED = 2026


class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 4, 3, padding=1)
        self.conv2 = nn.Conv2d(4, 8, 3, padding=1)
        self.fc = nn.Linear(8 * 7 * 7, 10)

    def trace(self, x):
        z1 = self.conv1(x)
        a1 = z1.relu()
        p1 = nn.functional.max_pool2d(a1, 2)
        z2 = self.conv2(p1)
        a2 = z2.relu()
        p2 = nn.functional.max_pool2d(a2, 2)
        flat = p2.flatten(1)
        logits = self.fc(flat)
        return dict(x=x, z1=z1, a1=a1, p1=p1, z2=z2, a2=a2,
                    p2=p2, flat=flat, logits=logits, probabilities=logits.softmax(1))

    def forward(self, x):
        return self.trace(x)['logits']


def main(path):
    torch.set_num_threads(4)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    source = np.load(path)
    x = torch.from_numpy(source['x_train'].copy()).float().unsqueeze(1) / 255
    y = torch.from_numpy(source['y_train'].astype(np.int64))
    test_x = torch.from_numpy(source['x_test'].copy()).float().unsqueeze(1) / 255
    test_y = torch.from_numpy(source['y_test'].astype(np.int64))
    model = CNN()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.CrossEntropyLoss()

    def evaluate(images, labels):
        total_loss = 0.0
        correct = 0
        with torch.no_grad():
            for start in range(0, len(labels), 256):
                output = model(images[start:start+256])
                target = labels[start:start+256]
                total_loss += nn.functional.cross_entropy(output, target, reduction='sum').item()
                correct += int((output.argmax(1) == target).sum())
        return dict(count=len(labels), correct=correct, accuracy=correct / len(labels),
                    cross_entropy=total_loss / len(labels))

    history = []
    for epoch in range(1, 5):
        permutation = torch.randperm(55000)
        total = 0.0
        model.train()
        for indices in permutation.split(128):
            optimizer.zero_grad()
            loss = loss_fn(model(x[indices]), y[indices])
            loss.backward()
            optimizer.step()
            total += loss.item() * len(indices)
        model.eval()
        row = dict(epoch=epoch, training_cross_entropy=total / 55000,
                   validation=evaluate(x[55000:], y[55000:]))
        history.append(row)
        print(json.dumps(row), flush=True)
    # Fixed index declared in advance, without searching for a favorable example.
    with torch.no_grad():
        trace = {k: v[0].numpy() for k, v in model.trace(test_x[:1]).items()}
    weights = {k.replace('.', '_'): v.detach().numpy() for k, v in model.state_dict().items()}
    np.savez_compressed(ROOT / 'trace.npz', **trace, **weights)
    test = evaluate(test_x, test_y)
    metadata = dict(seed=SEED, torch=torch.__version__, dataset_url=
        'https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz',
        dataset_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        preprocessing='float32 pixel / 255; no augmentation',
        splits=dict(train='original training indices 0:55000',
                    validation='original training indices 55000:60000', test='original test split'),
        optimizer=dict(name='Adam', learning_rate=0.001, batch_size=128, epochs=4),
        parameter_count=sum(p.numel() for p in model.parameters()),
        test_index=0, target=int(test_y[0]), prediction=int(trace['probabilities'].argmax()),
        sample_cross_entropy=float(-np.log(trace['probabilities'][int(test_y[0])])),
        history=history, test=test,
        trace_sha256=hashlib.sha256((ROOT / 'trace.npz').read_bytes()).hexdigest())
    (ROOT / 'training.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata), flush=True)


if __name__ == '__main__':
    main(Path(sys.argv[1]))
