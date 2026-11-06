"""Independently recompute the saved CNN using float64 NumPy operations."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent


def convolution(x, weights, bias):
    padded = np.pad(x.astype(np.float64), ((0, 0), (1, 1), (1, 1)))
    windows = np.lib.stride_tricks.sliding_window_view(padded, (3, 3), axis=(1, 2))
    return np.einsum('cijuv,ocuv->oij', windows, weights.astype(np.float64)) + bias[:, None, None]


def pool(x):
    c, h, w = x.shape
    return x.reshape(c, h//2, 2, w//2, 2).max(axis=(2, 4))


def main(dataset=None):
    data = np.load(ROOT / 'trace.npz')
    metadata = json.loads((ROOT / 'training.json').read_text())
    assert hashlib.sha256((ROOT / 'trace.npz').read_bytes()).hexdigest() == metadata['trace_sha256']
    values = dict(x=data['x'].astype(np.float64))
    for index in (1, 2):
        values[f'z{index}'] = convolution(values['x' if index == 1 else 'p1'],
            data[f'conv{index}_weight'], data[f'conv{index}_bias'])
        values[f'a{index}'] = np.maximum(values[f'z{index}'], 0)
        values[f'p{index}'] = pool(values[f'a{index}'])
    values['flat'] = values['p2'].flatten()
    values['logits'] = data['fc_weight'].astype(np.float64) @ values['flat'] + data['fc_bias']
    probabilities = np.exp(values['logits'] - values['logits'].max())
    values['probabilities'] = probabilities / probabilities.sum()
    errors = {}
    for key, value in values.items():
        np.testing.assert_allclose(value, data[key], atol=6e-6, rtol=6e-6)
        errors[key] = float(np.max(np.abs(value-data[key])))
    assert [data[k].shape for k in ('x','a1','p1','a2','p2','flat','logits')] == [
        (1,28,28),(4,28,28),(4,14,14),(8,14,14),(8,7,7),(392,),(10,)]
    count = sum(data[key].size for key in data.files if 'weight' in key or 'bias' in key)
    assert count == metadata['parameter_count'] == 4266
    loss = float(np.logaddexp.reduce(values['logits'])-values['logits'][metadata['target']])
    assert abs(loss-metadata['sample_cross_entropy']) < 1e-9
    assert values['probabilities'].argmax() == metadata['prediction'] == 7
    report = dict(trace_sha256=metadata['trace_sha256'], max_absolute_errors=errors,
                  independent_sample_cross_entropy=loss, parameter_count=count,
                  shapes={k:list(data[k].shape) for k in values})
    if dataset:
        path = Path(dataset)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == metadata['dataset_sha256']
        original = np.load(path)
        np.testing.assert_array_equal(data['x'][0], original['x_test'][0].astype(np.float32)/255)
        assert int(original['y_test'][0]) == metadata['target']
        # Reconstruct a separate model from exported parameters, verify held-out metrics.
        import torch
        from train import CNN
        torch.set_num_threads(4)
        model = CNN()
        model.load_state_dict({k:torch.from_numpy(data[k.replace('.', '_')].copy())
                               for k in model.state_dict()})
        model.eval()
        correct = 0
        total = 0.0
        with torch.no_grad():
            for start in range(0, 10000, 256):
                images = torch.from_numpy(original['x_test'][start:start+256].copy()).float().unsqueeze(1)/255
                targets = torch.from_numpy(original['y_test'][start:start+256].astype(np.int64))
                logits = model(images)
                correct += int((logits.argmax(1) == targets).sum())
                total += torch.nn.functional.cross_entropy(logits, targets, reduction='sum').item()
        assert correct == metadata['test']['correct']
        assert abs(total/10000-metadata['test']['cross_entropy']) < 1e-7
        report['dataset_verified'] = True
        report['test_recomputed'] = dict(correct=correct, count=10000, accuracy=correct/10000,
                                         cross_entropy=total/10000)
    (ROOT / 'numerical-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
