import subprocess
import sys


def test_cli_help():

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.bi_migrator",
            "--help",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "BI Migrator" in result.stdout
    assert "analyze" in result.stdout
