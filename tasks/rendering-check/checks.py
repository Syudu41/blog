"""Verify the algebra, GIF integrity, stage order, and final reading hold."""

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops

folder = Path(__file__).resolve().parent
artifact = folder / 'output/visualization.gif'
checksum = hashlib.sha256(artifact.read_bytes()).hexdigest()
source_checksum = hashlib.sha256((folder / 'scene.py').read_bytes()).hexdigest()
terms = {(1, 0): 1, (0, 1): 1}
expanded = {}
for (a1, b1), c1 in terms.items():
    for (a2, b2), c2 in terms.items():
        power = (a1 + a2, b1 + b2)
        expanded[power] = expanded.get(power, 0) + c1 * c2
assert expanded == {(2, 0): 1, (1, 1): 2, (0, 2): 1}
assert all((a+b)**2 == a*a + 2*a*b + b*b for a in range(-5, 6) for b in range(-5, 6))

storyboard_path = folder / 'storyboard.json'
for result_path in sorted((folder / 'runs').glob('*/result.json'), reverse=True):
    result = json.loads(result_path.read_text())
    if result.get('artifact_sha256') == checksum:
        run = result_path.parent
        request = json.loads((run / 'request.json').read_text())
        assert request['source_sha256'] == source_checksum
        storyboard = {'artifact_sha256': checksum, 'source_sha256': source_checksum,
                      'stages': json.loads((run / 'stages.json').read_text()),
                      'render_run': run.name, 'render_fps': result['settings']['fps'],
                      'tool_versions': result['environment']['tool_versions']}
        storyboard_path.write_text(json.dumps(storyboard, indent=2) + '\n')
        break
storyboard = json.loads(storyboard_path.read_text())
assert storyboard['artifact_sha256'] == checksum and storyboard['source_sha256'] == source_checksum
expected = ['square', 'factors', 'product-1', 'product-2', 'product-3', 'product-4',
            'distributed', 'expanded', 'matching-cross-terms', 'collected', 'final']
assert list(storyboard['stages']) == expected
assert storyboard['render_fps'] == 15
assert all(storyboard['stages'][left]['time'] < storyboard['stages'][right]['time']
           for left, right in zip(expected, expected[1:]))

frames = []
elapsed = 0
bounds = []
with Image.open(artifact) as reference_image:
    reference_image.seek(reference_image.n_frames - 1)
    reference = np.asarray(reference_image.convert('RGB')).astype(np.int16)
with Image.open(artifact) as image:
    assert image.format == 'GIF' and image.size == (960, 540)
    assert image.info.get('loop') == 0
    for index in range(image.n_frames):
        image.seek(index)
        image.load()
        assert image.size == (960, 540)
        duration = image.info.get('duration', 0) / 1000
        assert duration > 0
        rgb = image.convert('RGB')
        box = ImageChops.difference(rgb, Image.new('RGB', rgb.size, 'white')).getbbox()
        assert box and box[0] > 10 and box[1] > 10 and box[2] < 950 and box[3] < 530
        bounds.append(box)
        pixels = np.asarray(rgb).astype(np.int16)
        foreground = (reference.min(axis=2) < 240) | (pixels.min(axis=2) < 240)
        difference = np.abs(reference - pixels)
        # MP4-to-GIF encoding introduces tiny palette/background differences.
        # Test visible foreground stability rather than exact pixel identity.
        stable_final = (difference[foreground].mean() <= .25
                        and (difference.max(axis=2)[foreground] > 20).mean() <= .005)
        frames.append((elapsed, elapsed + duration, hashlib.sha256(rgb.tobytes()).hexdigest(), bool(stable_final)))
        elapsed += duration
stage_frames = {}
for name, stage in storyboard['stages'].items():
    frame = next(frame for frame in frames if frame[0] <= stage['time'] < frame[1])
    stage_frames[name] = frame[2]
assert len(set(stage_frames.values())) == len(expected), 'Each held stage must visibly differ'
final_hold = 0
for start, end, digest, stable in reversed(frames):
    if not stable:
        break
    final_hold += end - start
assert final_hold >= 2, final_hold
with Image.open(folder / 'output/thumbnail.png') as thumbnail:
    thumbnail.verify()
content = (folder / 'content.md').read_text().strip()
assert len(content.split('\n\n')) == 1 and len(content.split()) <= 60
assert 'https://www.3blue1brown.com/lessons/essence-of-calculus/' in content
report = {'passed': True, 'artifact_sha256': checksum, 'dimensions': [960, 540],
          'frames': len(frames), 'duration_seconds': elapsed, 'loop': 0, 'render_fps': 15,
          'final_hold_seconds': final_hold, 'stage_times': {key: value['time'] for key, value in storyboard['stages'].items()},
          'hold_tolerance': 'Foreground mean RGB difference <=0.25; at most 0.5% of foreground pixels differ by more than 20.',
          'stage_frame_hashes': stage_frames,
          'foreground_bounds': [min(b[0] for b in bounds), min(b[1] for b in bounds),
                                max(b[2] for b in bounds), max(b[3] for b in bounds)],
          'math': 'Exact polynomial coefficient expansion and 121 integer-pair checks passed.',
          'render_run': storyboard['render_run'], 'tool_versions': storyboard['tool_versions']}
(folder / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
