import traceback
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import psutil
from configobj import ConfigObj
from git import Repo


def print_diags(result: Any, tmp_path: Optional[Path] = None) -> None:
    """
    Print diagnostic information from a test result object.

    :param result:
        An object containing test results, expected to have the attributes
        ``output``, ``exception``, ``exc_info``, and ``exit_code``.
    :type result: Any
    :param tmp_path:
        Optional temporary directory, the contents of which will be printed.
    :type tmp_path: Path or None
    :return:
        This function does not return a value. It prints diagnostics to stdout.
    :rtype: None
    """
    print(f"Result : '{result.output}'")
    print(f"Exception : '{result.exception}'")
    print(f"Exception info : {result.exc_info}")
    traceback.print_tb(result.exc_info[2])
    print(f"Exit code : '{result.exit_code}'")
    if tmp_path is not None:
        print("Contents of tmp_path")
        for filename in [str(x) for x in tmp_path.rglob("*")]:
            print(filename)


def set_up_config(
    tmp_path: Path, configure_paths: bool = False
) -> Tuple[Path, Path, Path]:
    """
    Set up a configuration environment for testing.

    This function creates a configuration directory and files under the given
    temporary path. Optionally, it writes repository and CSR directory paths
    into the config file.

    :param tmp_path:
        Base temporary directory where configuration files and directories are created.
    :type tmp_path: Path
    :param configure_paths:
        Whether to configure ``repo_dir`` and ``csr_dir`` inside the config file.
    :type configure_paths: bool
    :return:
        A tuple containing paths to the orchestrator config file, the repository
        directory, and the CSR directory.
    :rtype: tuple[Path, Path, Path]
    """
    csr_dir = tmp_path / "csrs"
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    Path(tmp_path / ".config").mkdir()
    orchestrator_config_file = Path(tmp_path / ".config" / "config.ini")
    orchestrator_config_file.touch()

    if configure_paths:
        orchestrator_config = ConfigObj(str(orchestrator_config_file))
        orchestrator_config["repo_dir"] = repo_dir
        orchestrator_config["csr_dir"] = csr_dir
        orchestrator_config.write()

    return orchestrator_config_file, repo_dir, csr_dir


def set_up_environment(
    tmp_path: Path, datafiles: Path, monkeypatch: Optional[Any] = None
) -> Dict[str, Path]:
    """
    Set up a complete testing environment, including a git repository, certificate
    authorities, CSR files, and a simulated USB mount point. Also patches psutil
    to mock disk partitions.

    :param tmp_path:
        Base temporary directory where environment components will be created.
    :type tmp_path: Path
    :param datafiles:
        Path to directory containing test data files (e.g., ``example.csr``).
    :type datafiles: Path
    :param monkeypatch:
        Optional monkeypatching utility (pytest's ``monkeypatch`` fixture),
        used to replace ``psutil.disk_partitions`` with a fake implementation.
    :type monkeypatch: Any or None
    :return:
        A dictionary containing paths to environment components, with keys:
        ``repo_dir``, ``csr_dir``, ``cnf_file``, ``usb_mount_point``, and
        ``orchestrator_config_file``.
    :rtype: dict[str, Path]
    """
    orchestrator_config_file, repo_dir, csr_dir = set_up_config(
        tmp_path, configure_paths=True
    )
    csr_dir.mkdir()
    Path(repo_dir / ".git").mkdir()
    with Path(repo_dir / ".git" / "config").open("w") as f:
        f.write("[init]\n   defaultBranch = main\n")
    repo = Repo.init(repo_dir)
    Path(repo_dir / "certs_issued").mkdir()
    Path(repo_dir / "certs_issued" / "test").mkdir()
    Path(repo_dir / "certificate-authorities").mkdir()
    Path(repo_dir / "certificate-authorities" / "simple_test").mkdir()
    Path(repo_dir / "certificate-authorities" / "simple_test" / "test").mkdir()
    Path(
        repo_dir / "certificate-authorities" / "simple_test" / "test" / "test.crt"
    ).touch()
    with Path(
        repo_dir / "certificate-authorities" / "simple_test" / "test" / "serial"
    ).open("w") as f:
        f.write("01")
    with Path(
        repo_dir / "certificate-authorities" / "simple_test" / "test" / "index.txt"
    ).open("w") as f:
        f.write(
            "V\t22511013200827Z\t\t01\tunknown\t/C=US/O=Mozilla Corporation/OU=Mozilla"
            " AMO Production Signing Service/CN=test"
        )

    Path(repo_dir / "certificate-authorities" / "hwcrhk_foo").mkdir()
    Path(repo_dir / "certificate-authorities" / "hwcrhk_foo" / "foo").mkdir()
    Path(
        repo_dir / "certificate-authorities" / "hwcrhk_foo" / "foo" / "foo.crt"
    ).touch()
    with Path(
        repo_dir / "certificate-authorities" / "hwcrhk_foo" / "foo" / "serial"
    ).open("w") as f:
        f.write("01")
    with Path(
        repo_dir / "certificate-authorities" / "hwcrhk_foo" / "foo" / "index.txt"
    ).open("w") as f:
        f.write(
            "V\t22511013200827Z\t\t01\tunknown\t/C=US/O=Mozilla Corporation/OU=Mozilla"
            " AMO Production Signing Service/CN=test"
        )

    repo.index.commit("Setup repo")
    repo.create_head("main")
    csr_file = csr_dir / "example.csr"
    Path(datafiles / "example.csr").rename(csr_file)
    repo.create_remote("origin", "git@github.com:mozilla-services/hsm.git")
    feature_branch = repo.create_head("feature_branch")
    feature_branch.checkout()
    cnf_file = csr_dir / "example.cnf"

    # Mock up a fake USB flash drive
    usb_mount_point = tmp_path / "usb"
    usb_mount_point.mkdir()
    fake_partitions = [
        psutil._common.sdiskpart(
            device="/dev/sda1", mountpoint="/", fstype="ext4", opts="rw"
        ),
        psutil._common.sdiskpart(
            device="/dev/sdb1",
            mountpoint=str(usb_mount_point),
            fstype="exfat",
            opts="rw",
        ),
    ]

    def fake_disk_partitions(all: bool = False) -> Any:
        return fake_partitions

    if monkeypatch is not None:
        monkeypatch.setattr(psutil, "disk_partitions", fake_disk_partitions)

    return {
        "repo_dir": repo_dir,
        "csr_dir": csr_dir,
        "cnf_file": cnf_file,
        "usb_mount_point": usb_mount_point,
        "orchestrator_config_file": orchestrator_config_file,
    }
