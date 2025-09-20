import re
from pathlib import Path

import pytest
from click.testing import CliRunner
from rich.text import Text

from hsm_orchestrator import main
from .setup import set_up_environment

# from .setup import print_diags

FIXTURE_DIR = Path(__file__).parent.resolve() / "files"


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_selecting_usb_stick(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(datafiles / "example.cnf").rename(env["cnf_file"])
        keyboard_input = f"{env['usb_mount_point']}\n"
        result = runner.invoke(
            main,
            [
                "push-to-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert "Which mount is the USB stick you would you like to use" in result.output
        assert "Would you like to save this path" in result.output


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_save_usb_stick_to_config(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(datafiles / "example.cnf").rename(env["cnf_file"])
        keyboard_input = f"{env['usb_mount_point']}\ny\n"
        runner.invoke(
            main,
            [
                "push-to-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        with env["orchestrator_config_file"].open("r") as f:
            assert f"usb_stick_path = {env['usb_mount_point']}" in f.read()


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_read_usb_stick_mount_from_config(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(datafiles / "example.cnf").rename(env["cnf_file"])
        with env["orchestrator_config_file"].open("a") as f:
            f.write(f"usb_stick_path = {env['usb_mount_point']}\n")
        keyboard_input = "y\n"
        result = runner.invoke(
            main,
            [
                "push-to-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert (
            re.search(
                r"The instructions and files have been written to .*usb USB stick\.",
                Text.from_ansi(result.output).plain,
                flags=re.MULTILINE,
            )
            is not None
        )
        assert result.exit_code == 0


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_push(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(datafiles / "example.cnf").rename(env["cnf_file"])
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "push-to-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert "The instructions and files have been written to" in result.output
        assert result.exit_code == 0


# TODO : Add check that all files were copied
