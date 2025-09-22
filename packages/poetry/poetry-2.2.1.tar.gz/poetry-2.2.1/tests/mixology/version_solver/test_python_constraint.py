from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.factory import Factory
from tests.mixology.helpers import add_to_repo
from tests.mixology.helpers import check_solver_result


if TYPE_CHECKING:
    from poetry.core.packages.project_package import ProjectPackage

    from poetry.repositories import Repository
    from tests.mixology.version_solver.conftest import Provider


def test_dependency_does_not_match_root_python_constraint(
    root: ProjectPackage, provider: Provider, repo: Repository
) -> None:
    provider.set_package_python_versions("^3.6")
    root.add_dependency(Factory.create_dependency("foo", "*"))

    add_to_repo(repo, "foo", "1.0.0", python="<3.5")

    error = """\
The current project's supported Python range (>=3.6,<4.0) is not compatible with some\
 of the required packages Python requirement:
  - foo requires Python <3.5, so it will not be installable for Python >=3.6,<4.0

Because no versions of foo match !=1.0.0
 and foo (1.0.0) requires Python <3.5, foo is forbidden.
So, because myapp depends on foo (*), version solving failed.

  <fg=blue;options=bold>* </><fg=default;options=bold>Check your dependencies Python requirement</>: The Python requirement can be specified via the `<fg=default;options=bold>python</>` or `<fg=default;options=bold>markers</>` properties

    For <fg=default;options=bold>foo</>, a possible solution would be to set the `<fg=default;options=bold>python</>` property to <fg=yellow>"<empty>"</>

    <fg=blue>https://python-poetry.org/docs/dependency-specification/#python-restricted-dependencies</>,
    <fg=blue>https://python-poetry.org/docs/dependency-specification/#using-environment-markers</>
"""

    check_solver_result(root, provider, error=error)
