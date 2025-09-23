"""
CLI for usage
"""

import logging
import sys

from rich import print  # noqa
from tyro.extras import SubcommandApp

import cli_base
from cli_base import constants
from cli_base.autodiscover import import_all_files
from cli_base.cli_tools.shell_completion import fix_completion_prog
from cli_base.cli_tools.version_info import print_version


logger = logging.getLogger(__name__)

app = SubcommandApp()

# Register all CLI commands, just by import all files in this package:
import_all_files(package=__package__, init_file=__file__)


@app.command
def version():
    """Print version and exit"""
    # Pseudo command, because the version always printed on every CLI call ;)
    sys.exit(0)


def main():
    print_version(cli_base)
    app.cli(
        prog=fix_completion_prog('./cli.py'),
        description=constants.CLI_EPILOG,
        use_underscores=False,  # use hyphens instead of underscores
        sort_subcommands=True,
    )
