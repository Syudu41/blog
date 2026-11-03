"""Verify the identity algebraically and check the final figure's geometry."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops

folder = Path(__file__).resolve().parent
artifact = folder / "output/visualization.png"
terms = {(1, 0): 1, (0, 1): 1}
expanded = {}
for (a1, b1), c1 in terms.items():
    for (a2, b2), c2 in terms.items():
        power = (a1 + a2, b1 + b2)
        expanded[power] = expanded.get(power, 0) + c1 * c2
assert expanded == {(2, 0): 1, (1, 1): 2, (0, 2): 1}
assert all((a+b)**2 == a*a + 2*a*b + b*b for a in range(-5, 6) for b in range(-5, 6))
with Image.open(artifact) as image:
    image.load()
    assert image.size == (1800, 1200)
    assert all(abs(dpi - 300) < 1 for dpi in image.info["dpi"])
    rgb = image.convert("RGB")
    box = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).getbbox()
    assert box and box[0] > 20 and box[1] > 20 and box[2] < 1780 and box[3] < 1180
    dimensions = image.size
checksum = hashlib.sha256(artifact.read_bytes()).hexdigest()
report = {
    "passed": True, "artifact_sha256": checksum, "dimensions": dimensions,
    "dpi": 300, "foreground_bounds": box,
    "math": "Exact polynomial coefficient expansion passed, plus 121 integer-pair checks.",
}
for run in sorted((folder / "runs").glob("*/result.json"), reverse=True):
    data = json.loads(run.read_text())
    if data.get("artifact_sha256") == checksum:
        report["tool_versions"] = data["environment"]["tool_versions"]
        report["render_run"] = run.parent.name
        break
(folder / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
