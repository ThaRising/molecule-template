#!/usr/bin/env python
import os
from pathlib import Path
from typing import Optional

import pyaml
import yaml
from yaml.loader import SafeLoader

COOKIECUTTER_DIR = Path.cwd()
PROJECT_DIR = Path(COOKIECUTTER_DIR) / "{{cookiecutter.scenario_name}}"


def _remove_files(_files) -> None:
    for filename in _files:
        try:
            os.remove(PROJECT_DIR / filename)
        except FileNotFoundError:
            os.remove(COOKIECUTTER_DIR / filename)


def _list_files(glob: Optional[str] = "*") -> list:
    if PROJECT_DIR.exists():
        return [f for f in PROJECT_DIR.glob(glob)]
    else:
        return [f for f in COOKIECUTTER_DIR.glob(glob)]


if __name__ == '__main__':
    # Delete files that are exclusive to a specific driver
    cookiecutter_driver = "{{cookiecutter.driver}}"
    if not cookiecutter_driver == "docker":
        _remove_files(("Dockerfile.j2",))
    if not cookiecutter_driver == "kvm":
        _remove_files(("create.yml", "destroy.yml", "destroy_nvram.yml"))

    # Format Files
    files = _list_files("*.yml")
    for file in files:
        with open(file, "r") as fin:
            data = yaml.load(fin, Loader=SafeLoader)
        with open(file, "w") as fout:
            pyaml.dump(data, fout)
