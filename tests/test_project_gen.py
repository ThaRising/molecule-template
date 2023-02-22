import pytest
import logging
from pathlib import Path
import filecmp
from pytest_cookies.plugin import Result

logger = logging.getLogger(__name__)

def _build_error_msg(exc):
    return f"{exc.filename}: {exc.lineno}. MSG: {exc.message}"


def _test_ids(ctx: dict):
    _ctx = {k: (bool(v) if v in (0, 1) else v) for k, v in ctx.items()}
    return "-".join(f"{key}:{value}" for key, value in _ctx.items())


@pytest.fixture
def context():
    return {}


TEST_COMBINATIONS = [
    {"use_system_proxy": 0},
    {"use_system_proxy": 1},
    {"role_name": "myrole.ansible.v2"}
]


@pytest.mark.parametrize("context_override", TEST_COMBINATIONS, ids=_test_ids)
def test_bake_project(cookies, context, context_override):
    result: Result = cookies.bake(extra_context={**context, **context_override})

    assert result.exit_code == 0, _build_error_msg(result.exception)
    assert result.exception is None

    assert result.project_path.name == result.context.get("scenario_name")

    # E.g. 'role_name:myrole.ansible.v2'
    current_test_id = _test_ids(context_override)
    testfiles = Path.cwd() / "tests" / "files"
    current_testfile = testfiles / f"{current_test_id!s}__molecule.yml"

    assert filecmp.cmp(
        current_testfile, result.project_path / "molecule.yml", shallow=False
    )
