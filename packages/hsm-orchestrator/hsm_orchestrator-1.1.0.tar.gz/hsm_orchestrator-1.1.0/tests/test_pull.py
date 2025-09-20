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
def test_empty_usb_stick(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert "Which mount is the USB stick you would you like to use" in result.output
        assert (
            "No .crt files were found on the USB stick with names that match CA"
            " certificate files"
            in result.output
        )
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_multiple_ca_crt_files(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(env["usb_mount_point"] / "test.crt").touch()
        Path(env["usb_mount_point"] / "foo.crt").touch()
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert (
            "There are multiple .crt files on the USB stick with names that match CA"
            " certificate files"
            in result.output
        )
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_no_crt_files(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(env["usb_mount_point"] / "test.crt").touch()
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert (
            "There aren't any .crt files (other than the CA .crt file) on the USB"
            " stick."
            in Text.from_ansi(result.output).plain
        )
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_crt_related_files(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(env["usb_mount_point"] / "test.crt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.crt").touch()
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert (
            "The AUT-123-testing.crt file is missing some of the expected associated"
            " files"
            in Text.from_ansi(result.output).plain
        )
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_ca_related_files(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(env["usb_mount_point"] / "test.crt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.crt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.cnf").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.csr").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.output.txt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.instructions.txt").touch()
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert "Some of the expected CA files are missing" in result.output
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_file_actions_table_output(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(env["usb_mount_point"] / "test.crt").touch()
        Path(env["usb_mount_point"] / "serial").touch()
        Path(env["usb_mount_point"] / "index.txt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.crt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.cnf").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.csr").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.output.txt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.instructions.txt").touch()
        Path(env["usb_mount_point"] / "unrelated-file.txt").touch()
        Path(env["usb_mount_point"] / "unrelated-directory").mkdir()
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        result_lines = Text.from_ansi(result.output).plain.splitlines()
        assert any([
            re.match(r"^delete *: .*usb[/\\]test\.crt$", x) is not None
            for x in result_lines
        ])
        assert any([
            re.match(r"^delete *: .*usb[/\\]unrelated-file\.txt$", x) is not None
            for x in result_lines
        ])

        assert any([
            re.match(
                r".*repo[/\\]certs_issued[/\\]test *: .*usb[/\\]AUT-123-testing\.crt$",
                x,
            )
            is not None
            for x in result_lines
        ])
        assert any([
            re.match(
                r".*repo[/\\]certs_issued[/\\]test *: .*usb[/\\]AUT-123-testing\.csr$",
                x,
            )
            is not None
            for x in result_lines
        ])
        assert any([
            re.match(
                r".*repo[/\\]certs_issued[/\\]test *: .*usb[/\\]AUT-123-testing\.cnf$",
                x,
            )
            is not None
            for x in result_lines
        ])
        assert any([
            re.match(
                r".*repo[/\\]certs_issued[/\\]test *:"
                r" .*usb[/\\]AUT-123-testing\.output\.txt$",
                x,
            )
            is not None
            for x in result_lines
        ])
        assert any([
            re.match(
                r".*repo[/\\]certs_issued[/\\]test *:"
                r" .*usb[/\\]AUT-123-testing\.instructions\.txt$",
                x,
            )
            is not None
            for x in result_lines
        ])

        assert any([
            re.match(
                r".*repo[/\\]certificate-authorities[/\\]simple_test[/\\]test *:"
                r" .*usb[/\\]serial$",
                x,
            )
            is not None
            for x in result_lines
        ])
        assert any([
            re.match(
                r".*repo[/\\]certificate-authorities[/\\]simple_test[/\\]test *:"
                r" .*usb[/\\]index\.txt$",
                x,
            )
            is not None
            for x in result_lines
        ])

        assert any([
            re.match(r"ignore *: .*usb[/\\]unrelated-directory$", x) is not None
            for x in result_lines
        ])


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_file_actions(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(env["usb_mount_point"] / "test.crt").touch()
        Path(env["usb_mount_point"] / "serial").touch()
        Path(env["usb_mount_point"] / "index.txt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.crt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.cnf").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.csr").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.output.txt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.instructions.txt").touch()
        Path(env["usb_mount_point"] / "unrelated-file.txt").touch()
        Path(env["usb_mount_point"] / "unrelated-directory").mkdir()
        keyboard_input = f"{env['usb_mount_point']}\nn\ny\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert not Path(env["usb_mount_point"] / "test.crt").exists()
        assert not Path(env["usb_mount_point"] / "unrelated-file.txt").exists()
        assert not Path(env["usb_mount_point"] / "serial").exists()
        assert not Path(env["usb_mount_point"] / "index.txt").exists()
        assert not Path(env["usb_mount_point"] / "AUT-123-testing.crt").exists()
        assert not Path(env["usb_mount_point"] / "AUT-123-testing.cnf").exists()
        assert not Path(env["usb_mount_point"] / "AUT-123-testing.csr").exists()
        assert not Path(env["usb_mount_point"] / "AUT-123-testing.output.txt").exists()
        assert not Path(
            env["usb_mount_point"] / "AUT-123-testing.instructions.txt"
        ).exists()

        assert Path(env["usb_mount_point"] / "unrelated-directory").exists()
        ca_path = env["repo_dir"] / "certificate-authorities" / "simple_test" / "test"
        assert Path(ca_path / "serial").exists()
        assert Path(ca_path / "index.txt").exists()
        cert_path = env["repo_dir"] / "certs_issued" / "test"
        assert Path(cert_path / "AUT-123-testing.crt").exists()
        assert Path(cert_path / "AUT-123-testing.cnf").exists()
        assert Path(cert_path / "AUT-123-testing.csr").exists()
        assert Path(cert_path / "AUT-123-testing.output.txt").exists()
        assert Path(cert_path / "AUT-123-testing.instructions.txt").exists()
        assert result.exit_code == 0
