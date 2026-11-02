"""Supply the gallery catalog to the MkDocs template."""

import json
import runpy
from pathlib import Path


def on_config(config):
    workflow = Path(__file__).resolve().parents[1] / "scripts" / "visualization_workflow.py"
    runpy.run_path(str(workflow))["check_published"]()
    catalog = Path(config.docs_dir) / "catalog.json"
    config.extra["samples"] = json.loads(catalog.read_text())
    return config
