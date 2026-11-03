"""Decode the README GIF and export its recorded construction stages for review."""

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent


def main():
    artifact = ROOT / "output/visualization.gif"
    runs = sorted((ROOT / "runs").glob("*/result.json"))
    run = runs[-1].parent
    stages = json.loads((run / "stages.json").read_text())
    frames, times = [], []
    elapsed = 0
    with Image.open(artifact) as gif:
        assert gif.size == (960, 400)
        assert gif.info.get("loop") == 0
        for index in range(gif.n_frames):
            gif.seek(index)
            frames.append(gif.convert("RGB"))
            times.append(elapsed)
            elapsed += gif.info["duration"] / 1000
    assert len(frames) >= 100 and 7 <= elapsed <= 10
    assert artifact.stat().st_size < 5_000_000
    assert abs(len(frames) / elapsed - 15) < .2
    with Image.open(ROOT / "output/thumbnail.png") as thumbnail:
        assert thumbnail.size == (640, 267)
        thumbnail.verify()
    # Compression can perturb otherwise identical stills. Check the reset pose
    # with a small mean pixel tolerance, rather than expecting byte equality.
    reset_error = float(np.abs(np.array(frames[0], dtype=float)
                              - np.array(frames[-1], dtype=float)).mean())
    assert reset_error < 1
    sheet = Image.new("RGB", (1920, 1260), "white")
    draw = ImageDraw.Draw(sheet)
    for index, (name, seconds) in enumerate(stages.items()):
        nearest = min(range(len(times)), key=lambda i: abs(times[i] - seconds))
        x, y = (index % 2) * 960, (index // 2) * 420
        sheet.paste(frames[nearest], (x, y + 20))
        draw.text((x + 12, y + 3), f"{name}: {seconds:.2f}s", fill="black")
    sheet.save(ROOT / "review-stages.png")
    report = {
        "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "dimensions": [960, 400], "loop": 0, "frames": len(frames),
        "duration_seconds": round(elapsed, 3), "bytes": artifact.stat().st_size,
        "reset_mean_channel_error": reset_error, "stages": stages,
        "render_environment": json.loads((run / "result.json").read_text())["environment"],
    }
    (ROOT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items()
                      if key not in ("stages", "render_environment")}))


if __name__ == "__main__":
    main()
