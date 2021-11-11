import os

import pytest
import pyaml
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import filecmp


def _build_error_msg(exc):
    return f"{exc.filename}: {exc.lineno}. MSG: {exc.message}"


def _test_ids(ctx: dict):
    _ctx = {k: (bool(v) if v in (0, 1) else v) for k, v in ctx.items()}
    return "-".join(f"{key}:{value}" for key, value in _ctx.items())


@pytest.fixture
def context():
    return {
        "driver": "docker",
        "container_privileged": 0
    }


TEST_COMBINATIONS = [
    {"driver": "docker", "container_privileged": 0},
    {"driver": "docker", "container_privileged": 1},
    {"driver": "kvm"}
]


@pytest.mark.parametrize("context_override", TEST_COMBINATIONS, ids=_test_ids)
def test_bake_project(cookies, context, context_override):
    result = cookies.bake(extra_context={**context, **context_override})

    assert result.exit_code == 0, _build_error_msg(result.exception)
    assert result.exception is None

    assert result.project_path.name == result.context.get("scenario_name")
    if result.context.get("driver") == "kvm":
        # Test if all three files are present in the directory
        expected_files = {"create.yml", "destroy.yml", "destroy_nvram.yml"}
        assert len(
            expected_files.difference(set(os.listdir(result.project_path)))
        ) == 0
        # Make sure Dockerfile is not present when using KVM
        assert "Dockerfile.j2" not in os.listdir(result.project_path)

    current_test_id = _test_ids(context_override)
    testfiles = Path.cwd() / "tests" / "files"
    current_testfile = testfiles / f"{current_test_id!s}__molecule.yml"
    with open(current_testfile, "r") as fin:
        data = yaml.load(fin, Loader=SafeLoader)
    with open(current_testfile, "w") as fout:
        pyaml.dump(data, fout)

    assert filecmp.cmp(
        current_testfile, result.project_path / "molecule.yml", shallow=False
    )
