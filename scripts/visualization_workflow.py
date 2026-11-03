"""Prepare render reviews and publish only reviewed task outputs to Sphinx."""

import argparse
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ("render_success", "output_integrity", "mathematics", "latex_and_fonts", "layout", "visual_review")
IMAGES = {".png", ".gif", ".svg"}


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def task_file(folder, relative):
    path = (folder / relative).resolve()
    if not path.is_relative_to(folder.resolve()) or not path.is_file():
        raise ValueError(f"Missing or unsafe task file: {relative}")
    if path.stat().st_size == 0:
        raise ValueError(f"Empty task file: {relative}")
    return path


def load_task(folder):
    task = read_json(folder / "task.json")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", task["id"]):
        raise ValueError("Task id must be a lowercase hyphenated slug")
    for field in ("title", "description", "alt"):
        if not isinstance(task.get(field), str) or not task[field].strip():
            raise ValueError(f"Task needs {field}")
    requirements = task.get("requirements", [])
    if not requirements or len({r["id"] for r in requirements}) != len(requirements):
        raise ValueError("Task needs requirements with unique ids")
    if any(not r["id"].strip() or not r["description"].strip() for r in requirements):
        raise ValueError("Every requirement needs an id and description")
    if task_file(folder, task["source"]).suffix != ".py":
        raise ValueError("Task source must be editable Manim Python")
    if task_file(folder, task["output"]).suffix.lower() not in IMAGES | {".mp4"}:
        raise ValueError("Output must be PNG, GIF, SVG, or MP4")
    if task_file(folder, task["thumbnail"]).suffix.lower() not in IMAGES:
        raise ValueError("Thumbnail must be PNG, GIF, or SVG")
    task_file(folder, "requirements.md")
    return task


def hashes(folder, task):
    names = {"task.json", "requirements.md", "content.md", task["source"], task["output"], task["thumbnail"]}
    return {name: hashlib.sha256(task_file(folder, name).read_bytes()).hexdigest() for name in sorted(names)}


def prepare_review(folder):
    task = load_task(folder)
    target = folder / "review.json"
    if target.exists():
        raise ValueError("review.json already exists; archive the previous review before preparing another")
    def pending():
        return {"passed": False, "evidence": ""}
    write_json(target, {
        "status": "pending", "reviewer": "", "hashes": hashes(folder, task),
        "requirements": {r["id"]: pending() for r in task["requirements"]},
        "checks": {name: pending() for name in CHECKS},
    })


def validated_task(folder):
    task = load_task(folder)
    review = read_json(folder / "review.json")
    if review.get("status") != "passed" or not str(review.get("reviewer", "")).strip():
        raise ValueError("A completed review with a reviewer is required")
    if review.get("hashes") != hashes(folder, task):
        raise ValueError("Task or output changed after review; review the current files again")
    for group, expected in (("checks", set(CHECKS)), ("requirements", {r["id"] for r in task["requirements"]})):
        results = review.get(group, {})
        if set(results) != expected:
            raise ValueError(f"Review must cover every {group} entry")
        for name, result in results.items():
            evidence = result.get("evidence")
            if result.get("passed") is not True or not isinstance(evidence, str) or not evidence.strip():
                raise ValueError(f"Review did not pass {group}.{name} with evidence")
    return task


def catalog_entry(task):
    slug = task["id"]
    thumb = Path(task["thumbnail"]).suffix.lower()
    return {
        "id": slug, "title": task["title"], "subtitle": task.get("subtitle", ""),
        "description": task["description"], "page": f"{slug}/",
        "thumbnail": f"assets/{slug}/thumbnail{thumb}", "alt": task["alt"],
        "kind": "render", "task": slug,
    }


def page_content(folder, task):
    slug = task["id"]
    media = f"assets/{slug}/visualization{Path(task['output']).suffix.lower()}"
    escaped_media = html.escape(media, quote=True)
    alt = html.escape(task["alt"], quote=True)
    if media.endswith(".mp4"):
        thumbnail = catalog_entry(task)["thumbnail"]
        render = task.get("render", {})
        width, height = int(render.get("width", 1920)), int(render.get("height", 1080))
        if width <= 0 or height <= 0:
            raise ValueError("Video dimensions must be positive")
        visual = f'<video controls playsinline preload="metadata" width="{width}" height="{height}" style="aspect-ratio: {width} / {height};" poster="{thumbnail}" aria-label="{alt}"><source src="{escaped_media}" type="video/mp4">{alt}</video>'
    else:
        visual = f'<img src="{escaped_media}" alt="{alt}">'
    # Sphinx resolves Markdown images from their source document's directory.
    if not media.endswith(".mp4"):
        visual = f'![{task["alt"]}]({media})'
    else:
        visual = visual.replace('src="assets/', 'src="../assets/').replace('poster="assets/', 'poster="../assets/')
    title = html.escape(task["title"])
    content = (folder / "content.md").read_text().strip()
    return f"# {title}\n\n{visual}\n\n{content}\n\n[Download visualization]({media})\n\n[Back to sample visualizations](index.md)\n"


def publish(folder, root=ROOT):
    task = validated_task(folder)
    slug = task["id"]
    if folder.resolve() != (root / "tasks" / slug).resolve():
        raise ValueError("Publish from tasks/<task-id>/")
    task_file(folder, "content.md")
    gallery = root / "website" / "samples"
    catalog = read_json(gallery / "catalog.json")
    existing = next((item for item in catalog if item["id"] == slug), None)
    if existing and existing.get("task") != slug:
        raise ValueError("Choose a task id that does not overwrite a concept preview")
    if not existing and (gallery / f"{slug}.md").exists():
        raise ValueError("Choose a task id that does not overwrite an existing page")
    asset_dir = gallery / "assets" / slug
    asset_dir.mkdir(parents=True, exist_ok=True)
    for field, name in (("output", "visualization"), ("thumbnail", "thumbnail")):
        source = task_file(folder, task[field])
        shutil.copyfile(source, asset_dir / (name + source.suffix.lower()))
    (gallery / f"{slug}.md").write_text(page_content(folder, task))
    catalog = [item for item in catalog if item["id"] != slug] + [catalog_entry(task)]
    write_json(gallery / "catalog.json", catalog)


def check_published(root=ROOT):
    gallery = root / "website" / "samples"
    catalog = read_json(gallery / "catalog.json")
    if len({item["id"] for item in catalog}) != len(catalog):
        raise ValueError("Duplicate gallery ids")
    for item in catalog:
        if item.get("kind") == "concept":
            continue
        if item.get("kind") != "render" or item.get("task") != item["id"]:
            raise ValueError("Gallery renders must identify their task")
        slug = item["id"]
        folder = root / "tasks" / slug
        task = validated_task(folder)
        if task["id"] != slug or item != catalog_entry(task):
            raise ValueError(f"Gallery metadata differs from reviewed task {slug}")
        if (gallery / f"{slug}.md").read_text() != page_content(folder, task):
            raise ValueError(f"Detail page differs from task {slug}; republish it")
        for field, name in (("output", "visualization"), ("thumbnail", "thumbnail")):
            source = task_file(folder, task[field])
            published = gallery / "assets" / slug / (name + source.suffix.lower())
            if source.read_bytes() != published.read_bytes():
                raise ValueError(f"Published {field} differs from reviewed task {slug}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare-review", "publish", "check"))
    parser.add_argument("task", nargs="?", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "check":
            check_published()
        elif not args.task:
            parser.error("task folder is required")
        elif args.command == "prepare-review":
            prepare_review(args.task)
        else:
            publish(args.task)
        print(f"{args.command}: passed")
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, f"{args.command}: {error}\n")


if __name__ == "__main__":
    main()
