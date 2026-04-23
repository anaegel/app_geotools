import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

if importlib.util.find_spec("ug4py.pyugcore") is None:
    pytest.skip("ug4py is not installed; example script tests are skipped.", allow_module_level=True)

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize(
    "script_path",
    [
        ROOT / "example-python.py",
        ROOT / "example-tiff.py",
    ],
)
def test_example_scripts_run_without_error(script_path: Path) -> None:
    """Run example scripts and assert they exit successfully."""
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise AssertionError(
            f"Script {script_path.name} failed with return code {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    assert result.returncode == 0
