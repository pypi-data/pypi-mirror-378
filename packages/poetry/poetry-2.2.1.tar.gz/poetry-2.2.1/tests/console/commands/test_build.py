from __future__ import annotations

import shutil
import tarfile

from typing import TYPE_CHECKING

import pytest

from cleo.io.null_io import NullIO
from cleo.testers.application_tester import ApplicationTester

from poetry.console.application import Application
from poetry.console.commands.build import BuildCommand
from poetry.console.commands.build import BuildHandler
from poetry.console.commands.build import BuildOptions
from poetry.factory import Factory
from poetry.utils.helpers import remove_directory
from tests.helpers import with_working_directory


if TYPE_CHECKING:
    from pathlib import Path

    from cleo.testers.command_tester import CommandTester
    from pytest_mock import MockerFixture

    from poetry.poetry import Poetry
    from poetry.utils.env import VirtualEnv
    from tests.types import CommandTesterFactory
    from tests.types import FixtureDirGetter


@pytest.fixture
def tmp_project_path(tmp_path: Path) -> Path:
    return tmp_path / "project"


@pytest.fixture
def tmp_poetry(tmp_project_path: Path, fixture_dir: FixtureDirGetter) -> Poetry:
    # copy project so that we start with a clean directory
    shutil.copytree(fixture_dir("simple_project"), tmp_project_path)
    poetry = Factory().create_poetry(tmp_project_path)
    return poetry


@pytest.fixture
def tmp_tester(
    tmp_poetry: Poetry, command_tester_factory: CommandTesterFactory
) -> CommandTester:
    return command_tester_factory("build", tmp_poetry)


def get_package_glob(poetry: Poetry, local_version: str | None = None) -> str:
    version = poetry.package.version

    if local_version:
        version = version.replace(local=local_version)

    return f"{poetry.package.name.replace('-', '_')}-{version}*"


def test_build_format_is_not_valid(tmp_tester: CommandTester) -> None:
    with pytest.raises(ValueError, match=r"Invalid format.*"):
        tmp_tester.execute("--format not_valid")


@pytest.mark.parametrize("format", ["sdist", "wheel", "all"])
def test_build_creates_packages_in_dist_directory_if_no_output_is_specified(
    tmp_tester: CommandTester, tmp_project_path: Path, tmp_poetry: Poetry, format: str
) -> None:
    shutil.rmtree(tmp_project_path / "dist")
    tmp_tester.execute(f"--format {format}")
    build_artifacts = tuple(
        (tmp_project_path / "dist").glob(get_package_glob(tmp_poetry))
    )
    assert len(build_artifacts) > 0
    assert all(archive.exists() for archive in build_artifacts)


def test_build_with_local_version_label(
    tmp_tester: CommandTester, tmp_project_path: Path, tmp_poetry: Poetry
) -> None:
    shutil.rmtree(tmp_project_path / "dist")
    local_version_label = "local-version"
    tmp_tester.execute(f"--local-version {local_version_label}")
    build_artifacts = tuple(
        (tmp_project_path / "dist").glob(
            get_package_glob(tmp_poetry, local_version=local_version_label)
        )
    )

    assert len(build_artifacts) > 0
    assert all(archive.exists() for archive in build_artifacts)


@pytest.mark.parametrize("clean", [True, False])
def test_build_with_clean(
    tmp_tester: CommandTester, tmp_project_path: Path, tmp_poetry: Poetry, clean: bool
) -> None:
    dist_dir = tmp_project_path.joinpath("dist")
    dist_dir.joinpath("hello").touch(exist_ok=True)

    tmp_tester.execute("--clean" if clean else "")
    build_artifacts = tuple(dist_dir.glob("*"))

    assert len(build_artifacts) == 2 if clean else 3
    assert all(archive.exists() for archive in build_artifacts)


def test_build_with_clean_non_existing_output(
    tmp_tester: CommandTester, tmp_project_path: Path, tmp_poetry: Poetry
) -> None:
    dist_dir = tmp_project_path.joinpath("dist")

    remove_directory(dist_dir, force=True)
    assert not dist_dir.exists()

    tmp_tester.execute("--clean")
    build_artifacts = tuple(dist_dir.glob("*"))

    assert len(build_artifacts) == 2
    assert all(archive.exists() for archive in build_artifacts)


def test_build_not_possible_in_non_package_mode(
    fixture_dir: FixtureDirGetter,
    command_tester_factory: CommandTesterFactory,
) -> None:
    source_dir = fixture_dir("non_package_mode")

    poetry = Factory().create_poetry(source_dir)
    tester = command_tester_factory("build", poetry)

    assert tester.execute() == 1
    assert (
        tester.io.fetch_error()
        == "Building a package is not possible in non-package mode.\n"
    )


def test_build_with_multiple_readme_files(
    fixture_dir: FixtureDirGetter,
    tmp_path: Path,
    tmp_venv: VirtualEnv,
    command_tester_factory: CommandTesterFactory,
) -> None:
    source_dir = fixture_dir("with_multiple_readme_files")
    target_dir = tmp_path / "project"
    shutil.copytree(str(source_dir), str(target_dir))

    poetry = Factory().create_poetry(target_dir)
    tester = command_tester_factory("build", poetry, environment=tmp_venv)
    tester.execute()

    build_dir = target_dir / "dist"
    assert build_dir.exists()

    sdist_file = build_dir / "my_package-0.1.tar.gz"
    assert sdist_file.exists()
    assert sdist_file.stat().st_size > 0

    (wheel_file,) = build_dir.glob("my_package-0.1-*.whl")
    assert wheel_file.exists()
    assert wheel_file.stat().st_size > 0

    with tarfile.open(sdist_file) as tf:
        sdist_content = tf.getnames()

    assert "my_package-0.1/README-1.rst" in sdist_content
    assert "my_package-0.1/README-2.rst" in sdist_content


@pytest.mark.parametrize(
    "output_dir", [None, "dist", "test/dir", "../dist", "absolute"]
)
def test_build_output_option(
    tmp_tester: CommandTester,
    tmp_project_path: Path,
    tmp_poetry: Poetry,
    output_dir: str,
) -> None:
    shutil.rmtree(tmp_project_path / "dist")
    if output_dir is None:
        tmp_tester.execute()
        build_dir = tmp_project_path / "dist"
    elif output_dir == "absolute":
        tmp_tester.execute(f"--output {tmp_project_path / 'tmp/dist'}")
        build_dir = tmp_project_path / "tmp/dist"
    else:
        tmp_tester.execute(f"--output {output_dir}")
        build_dir = tmp_project_path / output_dir

    build_artifacts = tuple(build_dir.glob(get_package_glob(tmp_poetry)))
    assert len(build_artifacts) > 0
    assert all(archive.exists() for archive in build_artifacts)


def test_build_relative_directory_src_layout(
    tmp_path: Path, fixture_dir: FixtureDirGetter
) -> None:
    tmp_project_path = tmp_path / "project"
    with with_working_directory(fixture_dir("simple_project"), tmp_project_path):
        shutil.rmtree(tmp_project_path / "dist")
        (tmp_project_path / "src").mkdir()
        (tmp_project_path / "simple_project").rename(
            tmp_project_path / "src" / "simple_project"
        )

        # We have to use ApplicationTester because CommandTester
        # initializes Poetry before passing the directory.
        app = Application()
        tester = ApplicationTester(app)
        tester.execute("build --project .")

        build_dir = tmp_project_path / "dist"

        assert len(list(build_dir.iterdir())) == 2


def test_build_options_validate_formats() -> None:
    with pytest.raises(ValueError, match="Invalid format: UNKNOWN"):
        _ = BuildOptions(clean=True, formats=["sdist", "UNKNOWN"], output="dist")  # type: ignore[list-item]


def test_prepare_config_settings() -> None:
    config_settings = BuildCommand._prepare_config_settings(
        local_version="42",
        config_settings=["setting_1=value_1", "setting_2=value_2"],
        io=NullIO(),
    )

    assert config_settings == {
        "local-version": "42",
        "setting_1": "value_1",
        "setting_2": "value_2",
    }


def test_prepare_config_settings_raise_on_invalid_setting() -> None:
    with pytest.raises(ValueError, match="Invalid config setting format: value_2"):
        _ = BuildCommand._prepare_config_settings(
            local_version="42",
            config_settings=["setting_1=value_1", "value_2"],
            io=NullIO(),
        )


@pytest.mark.parametrize(
    ["fmt", "expected_formats"],
    [
        ("all", ["sdist", "wheel"]),
        (None, ["sdist", "wheel"]),
        ("sdist", ["sdist"]),
        ("wheel", ["wheel"]),
    ],
)
def test_prepare_formats(fmt: str | None, expected_formats: list[str]) -> None:
    formats = BuildCommand._prepare_formats(fmt)
    assert formats == expected_formats


@pytest.mark.parametrize(
    ["project", "isolated_build"],
    [
        ("core_in_range", False),
        ("core_not_in_range", True),
        ("has_build_script", True),
        ("multiple_build_deps", True),
        ("no_core", True),
        ("core_from_git", True),
        ("no_build_system", False),
        ("no_build_backend", False),
    ],
)
def test_requires_isolated_build(
    project: str,
    isolated_build: bool,
    fixture_dir: FixtureDirGetter,
    mocker: MockerFixture,
) -> None:
    poetry = Factory().create_poetry(fixture_dir(f"build_systems/{project}"))
    handler = BuildHandler(poetry=poetry, env=mocker.Mock(), io=NullIO())

    assert handler._requires_isolated_build() is isolated_build


def test_build_handler_build_isolated(
    fixture_dir: FixtureDirGetter, mocker: MockerFixture
) -> None:
    from build import ProjectBuilder

    poetry = Factory().create_poetry(fixture_dir("build_systems/has_build_script"))

    mock_builder = mocker.MagicMock(spec=ProjectBuilder)
    mock_isolated_builder = mocker.patch(
        "poetry.console.commands.build.isolated_builder"
    )
    mock_isolated_builder.return_value.__enter__.return_value = mock_builder

    handler = BuildHandler(poetry=poetry, env=mocker.Mock(), io=NullIO())
    handler.build(BuildOptions(clean=True, formats=["wheel"], output="dist"))

    assert mock_builder.build.call_count == 1
