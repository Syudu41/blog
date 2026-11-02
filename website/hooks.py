"""Supply the gallery catalog to the MkDocs template."""

import json
from pathlib import Path


def on_config(config):
    catalog = Path(config.docs_dir) / "catalog.json"
    config.extra["samples"] = json.loads(catalog.read_text())
    return config
