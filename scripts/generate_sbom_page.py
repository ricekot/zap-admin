#!/usr/bin/env python3

import requests
import sys
import yaml
from pathlib import Path

if len(sys.argv) != 2:
    print(f"USAGE: {sys.argv[0]} <CycloneDX SBOM JSON URL>")
    print(
        f"Example: {sys.argv[0]} https://github.com/zaproxy/zap-extensions/releases/download/webdriverwindows-v63/bom.json"
    )
    exit(1)

sbom_url = sys.argv[1]
sbom_json = requests.get(sbom_url).json()
addon_id = sbom_json["metadata"]["component"]["name"]

repo_root = Path(__file__).parent.parent.parent

with open(repo_root / "site" / "data" / "addons.yaml", "r") as f:
    addons_yaml = yaml.safe_load(f)
    addon_name = next(filter(lambda ao: ao["id"] == addon_id, addons_yaml))["name"]

result = {}
result["bomFormat"] = sbom_json["bomFormat"]
result["type"] = "sbom"
result["title"] = addon_name + " - SBOM"
result["components"] = []

for component in sbom_json["components"]:
    result_comp = {}
    result_comp["name"] = component["name"]
    result_comp["version"] = component["version"]
    result_comp["licenses"] = ", ".join(
        list(
            map(
                lambda m: m["license"].get("id") or m["license"].get("name"),
                component["licenses"],
            )
        )
    )
    result["components"].append(result_comp)

result_md = "---\n" + yaml.safe_dump(result) + "---\n"
with open(
    repo_root / "site" / "content" / "docs" / "sbom" / f"{addon_id}.md", "w"
) as f:
    f.write(result_md)
