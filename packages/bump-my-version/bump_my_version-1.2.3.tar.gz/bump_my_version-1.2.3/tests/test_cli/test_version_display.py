from click.testing import Result

from bumpversion import cli
from bumpversion import __version__


def test_version_displays_library_version(runner):
    """
    Arrange/Act: Run the `version` subcommand.

    Assert: The output matches the library version.
    """
    result: Result = runner.invoke(cli.cli, ["--version"])
    assert __version__ in result.output.strip(), "Version number should match library version."
