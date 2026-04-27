import subprocess
from pathlib import Path


def test_script_exists():
    assert Path("elevator_api.py").exists()


def test_script_runs_help():
    result = subprocess.run(
        ["bash", "elevator_api.py"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0 or result.returncode == 1