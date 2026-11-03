"""Check encoded media and the observed left-to-right activation sequence."""

import hashlib
import io
import json
import subprocess
from fractions import Fraction
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops

folder = Path(__file__).resolve().parent
artifact = folder / "output/visualization.mp4"
probe = json.loads(subprocess.run([
    "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(artifact)
], check=True, capture_output=True, text=True).stdout)
video = next(stream for stream in probe["streams"] if stream["codec_type"] == "video")
assert (video["width"], video["height"]) == (1920, 1080)
assert video["codec_name"] == "h264" and video["pix_fmt"] == "yuv420p"
assert Fraction(video["avg_frame_rate"]) == 30
assert abs(float(probe["format"]["duration"]) - 4.5) < .05
subprocess.run(["ffmpeg", "-v", "error", "-i", str(artifact), "-f", "null", "-"], check=True, capture_output=True)
positions = []
for time in (.8, 1.4, 2.0, 2.6, 3.2, 4.2):
    data = subprocess.run([
        "ffmpeg", "-v", "error", "-ss", str(time), "-i", str(artifact),
        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"
    ], check=True, capture_output=True).stdout
    image = Image.open(io.BytesIO(data)).convert("RGB")
    box = ImageChops.difference(image, Image.new("RGB", image.size, "white")).getbbox()
    assert box[0] > 20 and box[1] > 20 and box[2] < 1900 and box[3] < 1060
    pixels = np.asarray(image).astype(float)
    red, green, blue = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
    mask = (red > 1.4 * green) & (green > 25) & (blue < .6 * green)
    _, xs = np.nonzero(mask)
    if time < 4:
        assert len(xs) > 100
        positions.append(float(xs.mean() / image.width))
    else:
        assert len(xs) == 0, "The final hold should have no active highlight"
assert all(left < right for left, right in zip(positions, positions[1:]))
assert positions[0] < .35 and positions[-1] > .65
checksum = hashlib.sha256(artifact.read_bytes()).hexdigest()
report = {
    "passed": True, "artifact_sha256": checksum,
    "dimensions": [1920, 1080], "fps": 30, "duration_seconds": float(probe["format"]["duration"]),
    "codec": video["codec_name"], "pixel_format": video["pix_fmt"],
    "activation_x_at_seconds": {str(time): x for time, x in zip((.8, 1.4, 2., 2.6, 3.2), positions)},
    "final_hold": "No activation highlight at 4.2 seconds.",
}
for run in sorted((folder / "runs").glob("*/result.json"), reverse=True):
    data = json.loads(run.read_text())
    if data.get("artifact_sha256") == checksum:
        report["tool_versions"] = data["environment"]["tool_versions"]
        report["render_run"] = run.parent.name
        break
(folder / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
