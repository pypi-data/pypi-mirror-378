from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from cleo.exceptions import CleoNoSuchOptionError

from poetry.console.commands.sync import SyncCommand

# import all tests from the install command
# and run them for sync by overriding the command fixture
from tests.console.commands.test_install import *  # noqa: F403


if TYPE_CHECKING:
    from cleo.testers.command_tester import CommandTester
    from pytest_mock import MockerFixture


@pytest.fixture  # type: ignore[no-redef]
def command() -> str:
    return "sync"


@pytest.mark.skip("Only relevant for `poetry install`")  # type: ignore[no-redef]
def test_sync_option_is_passed_to_the_installer() -> None:
    """The only test from the install command that does not work for sync."""


def test_sync_option_not_available(tester: CommandTester) -> None:
    with pytest.raises(CleoNoSuchOptionError):
        tester.execute("--sync")


def test_synced_installer(tester: CommandTester, mocker: MockerFixture) -> None:
    assert isinstance(tester.command, SyncCommand)
    mock = mocker.patch(
        "poetry.console.commands.install.InstallCommand.installer",
        new_callable=mocker.PropertyMock,
    )

    tester.execute()

    mock.return_value.requires_synchronization.assert_called_with(True)
