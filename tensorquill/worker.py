"""Manim worker executed by the chosen render environment."""

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from fractions import Fraction
from pathlib import Path

MANIM_VERSION = "0.19.0"


def doctor(font):
    import manimpango
    import manim

    tools = {name: shutil.which(name) for name in ("ffmpeg", "ffprobe", "latex", "dvisvgm")}
    fonts = manimpango.list_fonts()
    result = {
        "manim": manim.__version__, "expected_manim": MANIM_VERSION,
        "tools": tools, "font": font, "font_available": font in fonts,
    }
    result["passed"] = all(tools.values()) and result["font_available"] and manim.__version__ == MANIM_VERSION
    if result["passed"]:
        try:
            with tempfile.TemporaryDirectory(prefix="tensorquill-tex-check-") as directory:
                with manim.tempconfig({"media_dir": directory}):
                    equation = manim.MathTex(r"x^2")
                    result["latex_smoke_test"] = bool(equation.width > 0)
        except Exception as error:
            result["latex_error"] = str(error)
            result["latex_smoke_test"] = False
        result["passed"] = result.get("latex_smoke_test", False)
    if result["passed"]:
        result["tool_versions"] = {name: external([name, "-version" if name == "ffmpeg" or name == "ffprobe" else "--version"]).splitlines()[0]
                                   for name in tools}
    return result


def external(command):
    return subprocess.run(command, check=True, capture_output=True, text=True, timeout=90).stdout


def inspect_media(path, settings):
    from PIL import Image

    fmt = settings["format"]
    if fmt in ("png", "gif"):
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            frames = getattr(image, "n_frames", 1)
            duration = 0
            for index in range(frames):
                image.seek(index)
                image.load()
                duration += image.info.get("duration", 0) / 1000
            result = {"format": image.format, "width": width, "height": height, "frames": frames, "duration": duration}
    else:
        data = json.loads(external(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))
        video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
        external(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"])
        result = {
            "format": "mp4", "codec": video["codec_name"], "width": video["width"], "height": video["height"],
            "fps": float(Fraction(video["avg_frame_rate"])), "duration": float(data["format"]["duration"]),
            "pixel_format": video["pix_fmt"],
        }
        if result["codec"] != "h264" or result["pixel_format"] != "yuv420p" or abs(result["fps"] - settings["fps"]) > .01:
            raise ValueError("MP4 codec or frame rate differs from the requested preset")
    if (result["width"], result["height"]) != (settings["width"], settings["height"]):
        raise ValueError("Output dimensions differ from the requested preset")
    if fmt != "png" and result["duration"] <= 0:
        raise ValueError("Animation has no playable duration")
    result["bytes"] = path.stat().st_size
    if result["bytes"] > settings["max_bytes"]:
        raise ValueError("Output exceeds the configured file-size limit")
    return result


def review_images(artifact, settings, run, media):
    from PIL import Image

    frames = []
    if settings["format"] == "mp4":
        for index, fraction in enumerate((.1, .5, .9)):
            path = run / f"review-{index}.png"
            external(["ffmpeg", "-v", "error", "-y", "-ss", str(media["duration"] * fraction),
                      "-i", str(artifact), "-frames:v", "1", str(path)])
            frames.append(path)
    elif settings["format"] == "gif":
        with Image.open(artifact) as image:
            for index, frame in enumerate((0, image.n_frames // 2, image.n_frames - 1)):
                image.seek(frame)
                path = run / f"review-{index}.png"
                image.convert("RGB").save(path)
                frames.append(path)
    else:
        frames = [artifact]
    with Image.open(frames[-1]) as image:
        image = image.convert("RGB")
        image.thumbnail((640, 640))
        image.save(run / "thumbnail.png")
    tiles = []
    for path in frames:
        with Image.open(path) as image:
            tile = image.convert("RGB")
            tile.thumbnail((600, 400))
            tiles.append(tile)
    sheet = Image.new("RGB", (sum(tile.width for tile in tiles), max(tile.height for tile in tiles)), "white")
    offset = 0
    for tile in tiles:
        sheet.paste(tile, (offset, 0))
        offset += tile.width
    sheet.save(run / "review-sheet.png")
    return [path.name for path in frames]


def render(request_path):
    import manim
    from PIL import Image

    request = json.loads(request_path.read_text())
    settings = request["settings"]
    run = Path(request["run"])
    preflight = doctor(settings["font"])
    if not preflight["passed"]:
        raise ValueError(f"Render environment is incomplete: {preflight}")
    manim.Text.set_default(font=settings["font"], color=manim.BLACK)
    manim.Tex.set_default(color=manim.BLACK)
    manim.MathTex.set_default(color=manim.BLACK)
    options = {
        "renderer": "cairo", "background_color": manim.WHITE,
        "pixel_width": settings["width"], "pixel_height": settings["height"],
        "frame_rate": settings["fps"], "frame_height": 8,
        "frame_width": 8 * settings["width"] / settings["height"],
        "media_dir": str(run / "media"), "output_file": "render",
        "save_last_frame": settings["format"] == "png", "write_to_movie": settings["format"] != "png",
        "format": "mp4", "disable_caching": True,
    }
    with manim.tempconfig(options):
        sys.path.insert(0, str(Path(request["source"]).parent))
        spec = importlib.util.spec_from_file_location("tensorquill_task_scene", request["source"])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        scene_class = getattr(module, settings["scene"])
        if not isinstance(scene_class, type) or not issubclass(scene_class, manim.Scene):
            raise ValueError("Requested scene is not a Manim Scene class")
        scene = scene_class(random_seed=settings["seed"])
        scene.render()
        writer = scene.renderer.file_writer
        source = Path(writer.image_file_path if settings["format"] == "png" else writer.movie_file_path)
    artifact = run / ("visualization." + settings["format"])
    if settings["format"] == "png":
        with Image.open(source) as image:
            image.save(artifact, dpi=(settings["dpi"], settings["dpi"]))
    elif settings["format"] == "gif":
        external(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-filter_complex",
                  f"fps={settings['fps']},split[a][b];[a]palettegen[p];[b][p]paletteuse", "-loop", "0", str(artifact)])
    else:
        # Put the MP4 index before the video data for progressive web playback.
        external(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-map", "0",
                  "-c", "copy", "-movflags", "+faststart", str(artifact)])
    media = inspect_media(artifact, settings)
    frames = review_images(artifact, settings, run, media)
    report = {
        "status": "passed", "scope": "render execution and media integrity only; requirement/visual review remains pending",
        "artifact": artifact.name, "thumbnail": "thumbnail.png", "review_sheet": "review-sheet.png",
        "review_frames": frames, "settings": settings, "media": media,
        "environment": preflight,
        "python": sys.version,
        "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "packages": {distribution.metadata["Name"]: distribution.version
                     for distribution in importlib.metadata.distributions() if distribution.metadata.get("Name")},
    }
    (run / "result.json").write_text(json.dumps(report, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("doctor")
    check.add_argument("--font", default="Liberation Sans")
    rendering = commands.add_parser("render")
    rendering.add_argument("request", type=Path)
    args = parser.parse_args()
    if args.command == "doctor":
        try:
            result = doctor(args.font)
        except ImportError as error:
            result = {"passed": False, "error": str(error), "action": "Create the render environment from environment.yml."}
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["passed"] else 1)
    try:
        render(args.request)
    except Exception:
        traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        # An interrupted PyAV encoder can keep interpreter-finalization threads
        # alive. This dedicated worker must report failure promptly to its parent.
        os._exit(1)


if __name__ == "__main__":
    main()
