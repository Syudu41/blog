"""Prepare render reviews and publish only reviewed task outputs to Sphinx."""

import argparse
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

import yaml

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
    current = hashes(folder, task)
    if review.get("hashes") != current:
        previous = review.get("hashes", {})
        changed = sorted(name for name in set(previous) | set(current) if previous.get(name) != current.get(name))
        raise ValueError(f"Task or output changed after review ({task['id']}: {', '.join(changed)}); review the current files again")
    for group, expected in (("checks", set(CHECKS)), ("requirements", {r["id"] for r in task["requirements"]})):
        results = review.get(group, {})
        if set(results) != expected:
            raise ValueError(f"Review must cover every {group} entry")
        for name, result in results.items():
            evidence = result.get("evidence")
            if result.get("passed") is not True or not isinstance(evidence, str) or not evidence.strip():
                raise ValueError(f"Review did not pass {group}.{name} with evidence")
    return task


def split_page(source):
    """Read a page's YAML front matter without changing its Markdown body."""
    if not source.startswith("---\n"):
        return {}, source
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", source, re.S)
    if not match:
        raise ValueError("Page front matter needs a closing --- line")
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid page front matter: {error}") from error
    if not isinstance(metadata, dict):
        raise ValueError("Page front matter must be a mapping")
    return metadata, source[match.end():].lstrip("\n")


def write_page(path, metadata, body):
    header = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True, width=10000).strip()
    path.write_text(f"---\n{header}\n---\n\n{body.strip()}\n")


def gallery_asset(gallery, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError(f"Invalid gallery asset: {relative}")
    path = (gallery / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(gallery.resolve()) or not path.is_file():
        raise ValueError(f"Missing or unsafe gallery asset: {relative}")
    return path


def gallery_entries(gallery):
    """Discover cards from authored Markdown; no separate catalog is required."""
    entries = []
    for path in sorted(gallery.glob("*.md")):
        if path.stem == "index":
            continue
        metadata, _ = split_page(path.read_text())
        if not {"task", "kind", "thumbnail", "media", "description"}.intersection(metadata):
            continue
        slug = path.stem
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"Invalid sample filename: {path.name}")
        for field in ("title", "description", "thumbnail", "alt"):
            value = metadata.get(field)
            if not isinstance(value, str) or not value.strip() or len(value.splitlines()) != 1:
                raise ValueError(f"{path.name} needs a single-line {field}")
        if not isinstance(metadata.get("subtitle", ""), str) or len(metadata.get("subtitle", "").splitlines()) > 1:
            raise ValueError(f"{path.name} needs a single-line subtitle")
        kind = metadata.get("kind", "render" if metadata.get("task") else None)
        if kind not in ("render", "concept"):
            raise ValueError(f"{path.name} needs a reviewed task, or explicit kind: concept for a non-render preview")
        if kind == "concept" and metadata.get("task"):
            raise ValueError(f"{path.name} cannot relabel a Manim task as a concept preview")
        for dimension in ("width", "height"):
            if dimension in metadata and (not isinstance(metadata[dimension], int) or isinstance(metadata[dimension], bool) or metadata[dimension] <= 0):
                raise ValueError(f"{path.name} {dimension} must be a positive integer")
        if kind == "render" and metadata.get("task") != slug:
            raise ValueError(f"{path.name} must reference its matching reviewed task: {slug}")
        if not isinstance(metadata.get("order", 10000), int) or isinstance(metadata.get("order"), bool):
            raise ValueError(f"{path.name} order must be an integer")
        if gallery_asset(gallery, metadata["thumbnail"]).suffix.lower() not in IMAGES:
            raise ValueError(f"{path.name} needs an image thumbnail")
        if kind == "render" and not metadata.get("media"):
            raise ValueError(f"{path.name} needs media")
        if metadata.get("media"):
            if gallery_asset(gallery, metadata["media"]).suffix.lower() not in IMAGES | {".mp4"}:
                raise ValueError(f"{path.name} has unsupported media")
        entry = dict(metadata, id=slug, page=f"{slug}/", kind=kind)
        entries.append(entry)
    return sorted(entries, key=lambda item: (item.get("order", 10000), item["id"]))


def task_assets(task):
    slug = task["id"]
    return {
        "media": f"assets/{slug}/visualization{Path(task['output']).suffix.lower()}",
        "thumbnail": f"assets/{slug}/thumbnail{Path(task['thumbnail']).suffix.lower()}",
    }


def render_page(source):
    """Insert the player at build time while leaving the authored file untouched."""
    metadata, body = split_page(source)
    media = metadata.get("media")
    visual = ""
    if media:
        alt = html.escape(metadata["alt"], quote=True)
        if media.endswith(".mp4"):
            width, height = metadata.get("width", 1920), metadata.get("height", 1080)
            visual = (f'<video controls controlslist="nodownload" playsinline preload="metadata" '
                      f'width="{width}" height="{height}" style="aspect-ratio: {width} / {height};" '
                      f'poster="../{html.escape(metadata["thumbnail"], quote=True)}" aria-label="{alt}">'
                      f'<source src="../{html.escape(media, quote=True)}" type="video/mp4">{alt}</video>')
        else:
            visual = f'![{metadata["alt"]}]({media})'
    title = "" if body.lstrip().startswith("# ") else f'# {metadata["title"]}\n\n'
    header = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True, width=10000).strip()
    return f"---\n{header}\n---\n\n{title}{visual}\n\n{body.strip()}\n\n[Back to sample visualizations](index.md)\n"


def publish(folder, root=ROOT):
    task = validated_task(folder)
    slug = task["id"]
    if folder.resolve() != (root / "tasks" / slug).resolve():
        raise ValueError("Publish from tasks/<task-id>/")
    gallery = root / "website" / "samples"
    page = gallery / f"{slug}.md"
    if page.exists():
        metadata, body = split_page(page.read_text())
        if metadata.get("task") != slug:
            raise ValueError("Choose a task id that does not overwrite an existing page")
    else:
        entries = gallery_entries(gallery)
        metadata = {"title": task["title"], "description": task["description"],
                    "alt": task["alt"], "task": slug,
                    "order": max((item.get("order", 0) for item in entries), default=0) + 10}
        if task.get("subtitle"):
            metadata["subtitle"] = task["subtitle"]
        body = task_file(folder, "content.md").read_text()
    # Publishing new media preserves the website author's wording and ordering.
    metadata.update(task_assets(task))
    if Path(task["output"]).suffix.lower() == ".mp4":
        metadata.update(width=task.get("render", {}).get("width", 1920),
                        height=task.get("render", {}).get("height", 1080))
    asset_dir = gallery / "assets" / slug
    asset_dir.mkdir(parents=True, exist_ok=True)
    for field, name in (("output", "visualization"), ("thumbnail", "thumbnail")):
        source = task_file(folder, task[field])
        shutil.copyfile(source, asset_dir / (name + source.suffix.lower()))
    write_page(page, metadata, body)


def check_published(root=ROOT):
    gallery = root / "website" / "samples"
    for item in gallery_entries(gallery):
        if item["kind"] == "concept":
            for field in ("media", "thumbnail"):
                parts = Path(item.get(field, "")).parts
                if len(parts) >= 3 and parts[0] == "assets" and (root / "tasks" / parts[1] / "task.json").exists():
                    raise ValueError("Manim task media must retain its reviewed task reference")
            continue
        slug = item["id"]
        folder = root / "tasks" / slug
        task = validated_task(folder)
        if task["id"] != slug:
            raise ValueError(f"Gallery task differs from reviewed task {slug}")
        for field, relative in task_assets(task).items():
            if item[field] != relative:
                raise ValueError(f"Gallery {field} differs from reviewed task {slug}")
        if item["media"].endswith(".mp4"):
            for dimension, default in (("width", 1920), ("height", 1080)):
                actual = item.get(dimension, default)
                expected = task.get("render", {}).get(dimension, default)
                if not isinstance(actual, int) or isinstance(actual, bool) or actual <= 0 or actual != expected:
                    raise ValueError(f"Gallery {dimension} differs from reviewed task {slug}")
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
