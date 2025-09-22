from __future__ import annotations

import re

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from urllib.parse import urlparse

import pytest


if TYPE_CHECKING:
    from collections.abc import Iterator

    import httpretty

    from httpretty.core import HTTPrettyRequest

    from tests.types import PythonHostedFileMocker


@pytest.fixture
def mock_files_python_hosted_factory(http: type[httpretty]) -> PythonHostedFileMocker:
    def factory(
        distribution_locations: list[Path], metadata_locations: list[Path]
    ) -> None:
        def file_callback(
            request: HTTPrettyRequest, uri: str, headers: dict[str, Any]
        ) -> list[int | dict[str, Any] | bytes | str]:
            name = Path(urlparse(uri).path).name

            locations = (
                metadata_locations
                if name.endswith(".metadata")
                else distribution_locations
            )

            for location in locations:
                fixture = location / name
                if fixture.exists():
                    return [200, headers, fixture.read_bytes()]

            return [404, headers, b"Not Found"]

        def mock_file_callback(
            request: HTTPrettyRequest, uri: str, headers: dict[str, Any]
        ) -> list[int | dict[str, Any] | bytes | str]:
            return [200, headers, b""]

        http.register_uri(
            http.GET,
            re.compile("^https://files.pythonhosted.org/.*$"),
            body=file_callback,
        )

        http.register_uri(
            http.GET,
            re.compile("^https://mock.pythonhosted.org/.*$"),
            body=mock_file_callback,
        )

    return factory


@pytest.fixture
def mock_files_python_hosted(
    mock_files_python_hosted_factory: PythonHostedFileMocker,
    package_distribution_locations: list[Path],
    package_metadata_locations: list[Path],
) -> Iterator[None]:
    mock_files_python_hosted_factory(
        distribution_locations=package_distribution_locations,
        metadata_locations=package_metadata_locations,
    )
    yield None
