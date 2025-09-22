from __future__ import annotations

import contextlib
import shutil
import uuid

from subprocess import CalledProcessError
from typing import TYPE_CHECKING
from zipfile import ZipFile

import pytest

from build import BuildBackendException
from build import ProjectBuilder
from packaging.metadata import parse_email
from pkginfo.distribution import NewMetadataVersion

from poetry.inspection.info import PackageInfo
from poetry.inspection.info import PackageInfoError
from poetry.utils.env import VirtualEnv


if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from packaging.metadata import RawMetadata
    from pytest_mock import MockerFixture

    from tests.types import FixtureDirGetter
    from tests.types import SetProjectContext


@pytest.fixture
def demo_sdist(fixture_dir: FixtureDirGetter) -> Path:
    return fixture_dir("distributions") / "demo-0.1.0.tar.gz"


@pytest.fixture
def demo_wheel(fixture_dir: FixtureDirGetter) -> Path:
    return fixture_dir("distributions") / "demo-0.1.0-py2.py3-none-any.whl"


@pytest.fixture
def demo_wheel_metadata(demo_wheel: Path) -> RawMetadata:
    with ZipFile(demo_wheel) as zf:
        metadata, _ = parse_email(zf.read("demo-0.1.0.dist-info/METADATA"))
    return metadata


@pytest.fixture
def source_dir(tmp_path: Path) -> Path:
    path = tmp_path / "source"
    path.mkdir()
    return path


@pytest.fixture
def demo_setup(source_dir: Path) -> Path:
    setup_py = source_dir / "setup.py"
    setup_py.write_text(
        "from setuptools import setup; "
        'setup(name="demo", '
        'version="0.1.0", '
        'install_requires=["package"])',
        encoding="utf-8",
    )
    return source_dir


@pytest.fixture
def demo_setup_cfg(source_dir: Path) -> Path:
    setup_cfg = source_dir / "setup.cfg"
    setup_cfg.write_text(
        "\n".join(
            [
                "[metadata]",
                "name = demo",
                "version = 0.1.0",
                "[options]",
                "install_requires = package",
            ]
        ),
        encoding="utf-8",
    )
    return source_dir


@pytest.fixture
def demo_setup_complex(source_dir: Path) -> Path:
    setup_py = source_dir / "setup.py"
    setup_py.write_text(
        "from setuptools import setup; "
        'setup(name="demo", '
        'version="0.1.0", '
        'install_requires=[i for i in ["package"]])',
        encoding="utf-8",
    )
    return source_dir


@pytest.fixture
def demo_setup_complex_pep517_legacy(demo_setup_complex: Path) -> Path:
    pyproject_toml = demo_setup_complex / "pyproject.toml"
    pyproject_toml.write_text(
        '[build-system]\nrequires = ["setuptools", "wheel"]', encoding="utf-8"
    )
    return demo_setup_complex


@pytest.fixture
def demo_setup_complex_calls_script(
    fixture_dir: FixtureDirGetter, source_dir: Path, tmp_path: Path
) -> Path:
    # make sure the scripts project is on the same drive (for Windows tests in CI)
    scripts_dir = tmp_path / "scripts"
    shutil.copytree(fixture_dir("scripts"), scripts_dir)

    pyproject = source_dir / "pyproject.toml"
    pyproject.write_text(
        f"""\
    [build-system]
    requires = ["setuptools", "scripts @ {scripts_dir.as_uri()}"]
    build-backend = "setuptools.build_meta:__legacy__"
""",
        encoding="utf-8",
    )

    setup_py = source_dir / "setup.py"
    setup_py.write_text(
        """\
import subprocess
from setuptools import setup
if subprocess.call(["exit-code"]) != 42:
    raise RuntimeError("Wrong exit code.")
setup(name="demo", version="0.1.0", install_requires=[i for i in ["package"]])
""",
        encoding="utf-8",
    )

    return source_dir


@pytest.fixture(autouse=True)
def use_project_context(set_project_context: SetProjectContext) -> Iterator[None]:
    with set_project_context("sample_project"):
        yield


def demo_check_info(info: PackageInfo, requires_dist: set[str] | None = None) -> None:
    assert info.name == "demo"
    assert info.version == "0.1.0"
    assert info.requires_dist

    if requires_dist:
        assert set(info.requires_dist) == requires_dist
    else:
        # Exact formatting various according to the exact mechanism used to extract the
        # metadata.
        assert set(info.requires_dist) in (
            {
                'cleo; extra == "foo"',
                "pendulum (>=1.4.4)",
                'tomlkit; extra == "bar"',
            },
            {
                'cleo ; extra == "foo"',
                "pendulum (>=1.4.4)",
                'tomlkit ; extra == "bar"',
            },
            {
                'cleo ; extra == "foo"',
                "pendulum>=1.4.4",
                'tomlkit ; extra == "bar"',
            },
            {
                "cleo ; extra == 'foo'",
                "pendulum (>=1.4.4)",
                "tomlkit ; extra == 'bar'",
            },
        )


def test_info_from_sdist(demo_sdist: Path) -> None:
    info = PackageInfo.from_sdist(demo_sdist)
    demo_check_info(info)
    assert info._source_type == "file"
    assert info._source_url == demo_sdist.resolve().as_posix()


def test_info_from_sdist_no_pkg_info(fixture_dir: FixtureDirGetter) -> None:
    path = fixture_dir("distributions") / "demo_no_pkg_info-0.1.0.tar.gz"
    info = PackageInfo.from_sdist(path)
    demo_check_info(info)
    assert info._source_type == "file"
    assert info._source_url == path.resolve().as_posix()


def test_info_from_wheel(demo_wheel: Path) -> None:
    info = PackageInfo.from_wheel(demo_wheel)
    demo_check_info(info)
    assert info._source_type == "file"
    assert info._source_url == demo_wheel.resolve().as_posix()


@pytest.mark.parametrize("version", ["23", "24", "299"])
def test_info_from_wheel_metadata_versions(
    version: str, fixture_dir: FixtureDirGetter
) -> None:
    path = (
        fixture_dir("distributions")
        / f"demo_metadata_version_{version}-0.1.0-py2.py3-none-any.whl"
    )
    with (
        pytest.warns(NewMetadataVersion)
        if version == "299"
        else contextlib.nullcontext()
    ):
        info = PackageInfo.from_wheel(path)
    demo_check_info(info)
    assert info._source_type == "file"
    assert info._source_url == path.resolve().as_posix()


def test_info_from_wheel_metadata_version_unknown(
    fixture_dir: FixtureDirGetter,
) -> None:
    path = (
        fixture_dir("distributions")
        / "demo_metadata_version_unknown-0.1.0-py2.py3-none-any.whl"
    )

    with pytest.warns(NewMetadataVersion), pytest.raises(PackageInfoError) as e:
        PackageInfo.from_wheel(path)

    assert "Unknown metadata version: 999.3" in str(e.value)


def test_info_from_wheel_metadata(demo_wheel_metadata: RawMetadata) -> None:
    info = PackageInfo.from_metadata(demo_wheel_metadata)
    demo_check_info(info)
    assert info.requires_python == ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*"
    assert info._source_type is None
    assert info._source_url is None


def test_info_from_wheel_metadata_incomplete() -> None:
    """
    To avoid differences in cached metadata,
    it is important that the representation of missing fields does not change!
    """
    metadata, _ = parse_email(b"Metadata-Version: 2.1\nName: demo\nVersion: 0.1.0\n")
    info = PackageInfo.from_metadata(metadata)
    assert info.name == "demo"
    assert info.version == "0.1.0"
    assert info.summary is None
    assert info.requires_dist is None
    assert info.requires_python is None


def test_info_from_bdist(demo_wheel: Path) -> None:
    info = PackageInfo.from_bdist(demo_wheel)
    demo_check_info(info)
    assert info._source_type == "file"
    assert info._source_url == demo_wheel.resolve().as_posix()


def test_info_from_poetry_directory(fixture_dir: FixtureDirGetter) -> None:
    info = PackageInfo.from_directory(fixture_dir("inspection") / "demo")
    demo_check_info(info)


def test_info_from_poetry_directory_fallback_on_poetry_create_error(
    mocker: MockerFixture, fixture_dir: FixtureDirGetter
) -> None:
    mock_create_poetry = mocker.patch(
        "poetry.inspection.info.Factory.create_poetry", side_effect=RuntimeError
    )
    mock_get_poetry_package = mocker.spy(PackageInfo, "_get_poetry_package")
    mock_get_pep517_metadata = mocker.patch(
        "poetry.inspection.info.get_pep517_metadata"
    )

    PackageInfo.from_directory(fixture_dir("inspection") / "demo_poetry_package")

    assert mock_create_poetry.call_count == 1
    assert mock_get_poetry_package.call_count == 1
    assert mock_get_pep517_metadata.call_count == 1


def test_info_from_requires_txt(fixture_dir: FixtureDirGetter) -> None:
    info = PackageInfo.from_metadata_directory(
        fixture_dir("inspection") / "demo_only_requires_txt.egg-info"
    )
    assert info is not None
    demo_check_info(info)


def test_info_no_setup_pkg_info_no_deps(fixture_dir: FixtureDirGetter) -> None:
    info = PackageInfo.from_metadata_directory(
        fixture_dir("inspection") / "demo_no_setup_pkg_info_no_deps"
    )
    assert info is not None
    assert info.name == "demo"
    assert info.version == "0.1.0"
    assert info.requires_dist is None


def test_info_no_setup_pkg_info_no_deps_for_sure(fixture_dir: FixtureDirGetter) -> None:
    info = PackageInfo.from_metadata_directory(
        fixture_dir("inspection") / "demo_no_setup_pkg_info_no_deps_for_sure",
    )
    assert info is not None
    assert info.name == "demo"
    assert info.version == "0.1.0"
    assert info.requires_dist == []


def test_info_no_setup_pkg_info_no_deps_dynamic(fixture_dir: FixtureDirGetter) -> None:
    info = PackageInfo.from_metadata_directory(
        fixture_dir("inspection") / "demo_no_setup_pkg_info_no_deps_dynamic",
    )
    assert info is not None
    assert info.name == "demo"
    assert info.version == "0.1.0"
    assert info.requires_dist is None


def test_info_setup_simple(mocker: MockerFixture, demo_setup: Path) -> None:
    spy = mocker.spy(VirtualEnv, "run")
    info = PackageInfo.from_directory(demo_setup)

    assert spy.call_count == 6
    demo_check_info(info, requires_dist={"package"})


def test_info_setup_complex(demo_setup_complex: Path) -> None:
    info = PackageInfo.from_directory(demo_setup_complex)
    demo_check_info(info, requires_dist={"package"})


def test_info_setup_complex_pep517_error(
    mocker: MockerFixture, demo_setup_complex: Path
) -> None:
    output = uuid.uuid4().hex
    mocker.patch(
        "build.ProjectBuilder.from_isolated_env",
        autospec=True,
        side_effect=BuildBackendException(CalledProcessError(1, "mock", output=output)),
    )

    with pytest.raises(PackageInfoError) as exc:
        PackageInfo.from_directory(demo_setup_complex)

    text = str(exc.value)
    assert "Command 'mock' returned non-zero exit status 1." in text
    assert output in text
    assert (
        "This error originates from the build backend, and is likely not a problem with poetry"
        in text
    )


def test_info_setup_complex_pep517_legacy(
    demo_setup_complex_pep517_legacy: Path,
) -> None:
    info = PackageInfo.from_directory(demo_setup_complex_pep517_legacy)
    demo_check_info(info, requires_dist={"package"})


def test_info_setup_complex_calls_script(demo_setup_complex_calls_script: Path) -> None:
    """Building the project requires calling a script from its build_requires."""
    info = PackageInfo.from_directory(demo_setup_complex_calls_script)
    demo_check_info(info, requires_dist={"package"})


@pytest.mark.parametrize("missing", ["version", "name"])
def test_info_setup_missing_mandatory_should_trigger_pep517(
    mocker: MockerFixture, source_dir: Path, missing: str
) -> None:
    setup = "from setuptools import setup; "
    setup += "setup("
    setup += 'name="demo", ' if missing != "name" else ""
    setup += 'version="0.1.0", ' if missing != "version" else ""
    setup += 'install_requires=["package"]'
    setup += ")"

    setup_py = source_dir / "setup.py"
    setup_py.write_text(setup, encoding="utf-8")

    spy = mocker.spy(ProjectBuilder, "from_isolated_env")
    _ = PackageInfo.from_directory(source_dir)
    assert spy.call_count == 1


def test_info_prefer_poetry_config_over_egg_info(fixture_dir: FixtureDirGetter) -> None:
    info = PackageInfo.from_directory(
        fixture_dir("inspection") / "demo_with_obsolete_egg_info"
    )
    demo_check_info(info)
