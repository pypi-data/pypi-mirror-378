import logging
from pathlib import Path
import sys

from rich import print  # noqa

from cli_base.cli_app import app
from cli_base.cli_tools import git_history
from cli_base.cli_tools.verbosity import setup_logging
from cli_base.tyro_commands import TyroVerbosityArgType


logger = logging.getLogger(__name__)


@app.command
def update_readme_history(auto_commit: bool = True, verbosity: TyroVerbosityArgType = 1) -> None:
    """
    Update project history base on git commits/tags in README.md

    Will be exited with 1 if the README.md was updated otherwise with 0.

    Also, callable via e.g.:
        python -m cli_base update-readme-history -v
    """
    setup_logging(verbosity=verbosity)

    logger.debug('%s called. CWD: %s', __name__, Path.cwd())
    updated = git_history.update_readme_history(
        auto_commit=auto_commit,
        verbosity=verbosity,
    )
    if auto_commit:
        logger.info('Auto commit is enabled. Always exit with 0.')
        exit_code = 0
    else:
        exit_code = 1 if updated else 0
    if verbosity:
        print(f'{exit_code=}')
    sys.exit(exit_code)
