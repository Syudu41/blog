"""Task creation and bounded rendering, without a model API."""

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMATS = {".png": "png", ".mp4": "mp4", ".gif": "gif"}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def safe_path(folder, name):
    path = (folder / name).resolve()
    if not path.is_relative_to(folder.resolve()):
        raise ValueError(f"Task path escapes its folder: {name}")
    return path


def create_task(slug, request, title=None, output_format="png", root=ROOT):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Use a lowercase, hyphenated task id")
    if not request.strip():
        raise ValueError("A task request is required")
    folder = root / "tasks" / slug
    folder.mkdir(parents=True, exist_ok=False)
    title = title or slug.replace("-", " ").capitalize()
    write_json(folder / "task.json", {
        "id": slug, "title": title, "description": f"A visualization of {title.lower()}.",
        "alt": f"Visualization of {title.lower()}.", "source": "scene.py",
        "output": f"output/visualization.{output_format}", "thumbnail": "output/thumbnail.png",
        "render": {"scene": "Visualization", "font": "Liberation Sans", "seed": 42},
        "requirements": [
            {"id": "content", "description": request.strip()},
            {"id": "format", "description": f"Produce a valid {output_format.upper()} file and PNG thumbnail."},
            {"id": "typography", "description": "Use LaTeX for all math and Arial-family prose."},
        ],
    })
    (folder / "requirements.md").write_text(f"# {title}\n\n{request.strip()}\n")
    (folder / "content.md").write_text(f"Explain the visualization of {title.lower()} here before review.\n")
    (folder / "scene.py").write_text(
        'from manim import Scene\n\n\nclass Visualization(Scene):\n'
        '    def construct(self):\n'
        '        raise NotImplementedError("Write the scene to match requirements.md before rendering.")\n'
    )
    return folder


def settings_for(task, preset, output_format=None):
    fmt = output_format or FORMATS.get(Path(task["output"]).suffix.lower())
    if fmt is None:
        raise ValueError("Rendering supports PNG, MP4, and GIF; SVG publication figures need a separate vector-export pipeline")
    options = task.get("render", {})
    defaults = {"png": (1800, 1200, 30), "mp4": (1920, 1080, 30), "gif": (960, 540, 15)}
    width, height, fps = defaults[fmt]
    width = options.get("width", width)
    height = options.get("height", height)
    fps = options.get("fps", fps)
    if any(not isinstance(v, int) or isinstance(v, bool) or v <= 0 for v in (width, height, fps)):
        raise ValueError("Render width, height, and fps must be positive integers")
    if width > 7680 or height > 7680 or fps > 120:
        raise ValueError("Render settings exceed the supported resolution/frame-rate limits")
    if preset == "draft":
        width, height = max(2, width // 4 * 2), max(2, height // 4 * 2)
        fps = min(fps, 15)
    if fmt != "png" and (width % 2 or height % 2):
        raise ValueError("Video and GIF dimensions must be even")
    if not isinstance(options.get("dpi", 300), int) or not 72 <= options.get("dpi", 300) <= 1200:
        raise ValueError("DPI must be an integer between 72 and 1200")
    max_bytes = options.get("max_bytes", 20_000_000 if fmt == "gif" else 100_000_000)
    if not isinstance(max_bytes, int) or max_bytes <= 0:
        raise ValueError("Maximum output size must be a positive integer in bytes")
    return {
        "format": fmt, "width": width, "height": height, "fps": fps,
        "font": options.get("font", "Liberation Sans"), "seed": options.get("seed", 42),
        "scene": options.get("scene", "Visualization"), "dpi": options.get("dpi", 300), "max_bytes": max_bytes,
    }


def worker_command(python, *arguments):
    executable = shutil.which(python) or str(Path(python).resolve())
    if not Path(executable).is_file():
        raise ValueError(f"Render Python not found: {python}")
    return [executable, "-m", "tensorquill.worker", *map(str, arguments)]


def worker_environment(python):
    # Do not forward model, GitHub, cloud, or deployment tokens to scene processes.
    allowed = ("HOME", "LANG", "LC_ALL", "DISPLAY", "FONTCONFIG_PATH", "FONTCONFIG_FILE")
    environment = {key: os.environ[key] for key in allowed if key in os.environ}
    bins = [str(Path(python).resolve().parent)]
    if os.environ.get("TENSORQUILL_TEX_BIN"):
        bins.insert(0, os.environ["TENSORQUILL_TEX_BIN"])
    environment["PATH"] = os.pathsep.join(bins) + os.pathsep + os.environ.get("PATH", "")
    cache = Path(tempfile.gettempdir()) / "tensorquill-cache"
    cache.mkdir(exist_ok=True)
    environment["XDG_CACHE_HOME"] = str(cache)
    environment["MPLCONFIGDIR"] = str(cache / "matplotlib")
    environment["PYTHONUNBUFFERED"] = "1"
    return environment


def run_worker(command, log, timeout):
    with log.open("w") as stream:
        process = subprocess.Popen(command, cwd=ROOT, env=worker_environment(command[0]),
                                   stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
            if code:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            return code
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            raise ValueError(f"Render exceeded {timeout} seconds; see {log}")


def render_task(folder, python=sys.executable, preset="draft", timeout=180, output_format=None):
    folder = folder.resolve()
    task = json.loads((folder / "task.json").read_text())
    source = safe_path(folder, task["source"])
    if not source.is_file():
        raise ValueError(f"Scene source is missing: {source}")
    settings = settings_for(task, preset, output_format)
    primary = settings["format"] == FORMATS.get(Path(task["output"]).suffix.lower())
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    run = folder / "runs" / stamp
    run.mkdir(parents=True)
    request = {
        "source": str(source), "run": str(run), "settings": settings,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "requirements_sha256": hashlib.sha256((folder / "requirements.md").read_bytes()).hexdigest(),
        "task_sha256": hashlib.sha256((folder / "task.json").read_bytes()).hexdigest(),
        "preset": preset, "primary_output": primary,
    }
    write_json(run / "request.json", request)
    command = worker_command(python, "render", run / "request.json")
    try:
        code = run_worker(command, run / "render.log", timeout)
        if code != 0:
            raise ValueError(f"Render failed with exit code {code}; see {run / 'render.log'}")
        report = json.loads((run / "result.json").read_text())
        if report.get("status") != "passed":
            raise ValueError(f"Media checks did not pass; see {run / 'result.json'}")
        for key, path in (("source_sha256", source), ("requirements_sha256", folder / "requirements.md"),
                          ("task_sha256", folder / "task.json")):
            if request[key] != hashlib.sha256(path.read_bytes()).hexdigest():
                raise ValueError("Task input changed during rendering")
        if preset == "final" and primary:
            for field, artifact in (("output", "artifact"), ("thumbnail", "thumbnail")):
                target = safe_path(folder, task[field])
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(run / report[artifact], target)
            review = folder / "review.json"
            if review.exists():
                shutil.move(str(review), run / "review.previous.json")
        print(f"Render and media checks passed: {run}")
        print("Inspect the artifact and review frames against requirements.md before publication.")
        return run
    except (ValueError, OSError, KeyError) as error:
        write_json(run / "failure.json", {"status": "failed", "error": str(error)})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("new", help="Create a task folder; the coding agent then writes its scene")
    new.add_argument("id")
    new.add_argument("--request-file", type=Path, required=True)
    new.add_argument("--title")
    new.add_argument("--format", choices=("png", "mp4", "gif"), default="png")
    doctor = commands.add_parser("doctor", help="Check Manim, LaTeX, fonts, and media tools")
    doctor.add_argument("--python", default=sys.executable)
    doctor.add_argument("--font", default="Liberation Sans")
    render = commands.add_parser("render", help="Render a task and validate its media")
    render.add_argument("task", type=Path)
    render.add_argument("--python", default=sys.executable)
    render.add_argument("--preset", choices=("draft", "final"), default="draft")
    render.add_argument("--format", choices=("png", "mp4", "gif"), help="Render a companion format into the run folder")
    render.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    try:
        if args.command == "new":
            print(create_task(args.id, args.request_file.read_text(), args.title, args.format))
        elif args.command == "doctor":
            command = worker_command(args.python, "doctor", "--font", args.font)
            raise SystemExit(subprocess.call(command, cwd=ROOT, env=worker_environment(command[0])))
        else:
            if args.timeout <= 0:
                raise ValueError("Timeout must be positive")
            render_task(args.task, args.python, args.preset, args.timeout, args.format)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"tensorquill: {error}\n")
