from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

from bx_py_utils.path import assert_is_dir, assert_is_file
from rich import print  # noqa
from rich.console import Console

from cli_base.cli_tools.path_utils import which
from cli_base.cli_tools.rich_utils import human_error
from cli_base.constants import PY_BIN_PATH


DEFAULT_TIMEOUT = 15 * 60  # 15 minutes


def make_absolute_path(path):
    """
    Resolve the path, but not for symlinks.
    e.g.: '.venv/bin/python' is a symlink to e.g.: '/usr/bin/python3.x'
    We would like to keep the origin symlink ;)
    """
    if not isinstance(path, Path):
        path = Path(path)

    if path.is_symlink():
        path = path.absolute()
    else:
        path = path.resolve(strict=True)

    return path


def make_relative_path(path, relative_to):
    """
    Makes {path} relative to {relative_to}, if possible.
    """
    path = make_absolute_path(path=path)
    relative_to = make_absolute_path(path=relative_to)

    try:
        is_relative_to = path.is_relative_to(relative_to)
    except AttributeError:  # is_relative_to() is new in Python 3.9
        try:
            path = path.relative_to(relative_to)
        except ValueError:
            # {path} doesn't start with {relative_to} -> do nothing
            pass
    else:
        if is_relative_to:
            path = path.relative_to(relative_to)

    return path


def _print_info(
    popenargs,
    *,
    cwd,
    kwargs,
    console: Console | None = None,
):
    console = console or Console()
    console.rule(characters='_')

    if len(popenargs) > 1:
        command, *args = popenargs
    else:
        command = popenargs[0]
        args = []

    command_path = make_relative_path(Path(command), relative_to=cwd)

    command_name = command_path.name
    command_dir = command_path.parent

    print(f'[white]{cwd}[/white][bold]$[/bold]', end=' ')

    if command_dir and command_dir != Path.cwd():
        print(f'[green]{command_dir}{os.sep}[/green]', end='')

    if command_name:
        print(f'[yellow bold]{command_name}[/yellow bold]', end='')

    for arg in args:
        if isinstance(arg, str):
            if arg.startswith('--'):
                print(f' [magenta]{arg}[/magenta]', end='')
                continue
            elif arg.startswith('-'):
                print(f' [cyan]{arg}[/cyan]', end='')
                continue

        print(f' [blue]{arg}[/blue]', end='')

    if kwargs:
        verbose_kwargs = ', '.join(f'{k}={v!r}' for k, v in sorted(kwargs.items()))
        print(f' (kwargs: {verbose_kwargs})', end='')

    print('\n', flush=True)


def prepare_popenargs(popenargs, cwd=None):
    if cwd is None:
        cwd = Path.cwd()
    else:
        assert_is_dir(cwd)

    command_path = Path(popenargs[0])
    if not command_path.is_file():
        # Lookup in current venv bin path first:
        command = which(str(command_path))
        if not command:
            raise FileNotFoundError(f'Command "{popenargs[0]}" not found in PATH!')

        command = make_absolute_path(path=command)

        # Replace command name with full path:
        popenargs = list(popenargs)
        popenargs[0] = command

    return popenargs, cwd


def verbose_check_call(
    *popenargs,
    verbose=True,
    cwd=None,
    extra_env=None,
    exit_on_error=False,
    timeout=DEFAULT_TIMEOUT,
    env=None,
    text=True,
    **kwargs,
):
    """
    'verbose' version of subprocess.check_call()
    Will try to find the command in current Python venv/bin/ path
    """

    popenargs, cwd = prepare_popenargs(popenargs, cwd=cwd)

    if verbose:
        _print_info(popenargs, cwd=cwd, kwargs=kwargs)

    if env is None:
        env = os.environ.copy()

    if extra_env:
        env.update(extra_env)

    try:
        return subprocess.check_call(
            [str(part) for part in popenargs],  # e.g.: Path() instance -> str,
            text=text,
            env=env,
            cwd=cwd,
            timeout=timeout,
            **kwargs,
        )
    except subprocess.CalledProcessError as err:
        if verbose:
            print(f'[red]Process "{popenargs[0]}" finished with exit code {err.returncode!r}[/red]')
        if exit_on_error:
            sys.exit(err.returncode)
        raise


def verbose_check_output(
    *popenargs,
    verbose=True,
    cwd=None,
    extra_env=None,
    exit_on_error=False,
    print_output_on_error=True,
    timeout=DEFAULT_TIMEOUT,
    env=None,
    text=True,
    **kwargs,
):
    """
    'verbose' version of subprocess.check_output()
    Will try to find the command in current Python venv/bin/ path
    """

    popenargs, cwd = prepare_popenargs(popenargs, cwd=cwd)

    if verbose:
        _print_info(popenargs, cwd=cwd, kwargs=kwargs)

    if env is None:
        env = os.environ.copy()

    if extra_env:
        env.update(extra_env)

    try:
        output = subprocess.check_output(
            [str(part) for part in popenargs],  # e.g.: Path() instance -> str,
            text=text,
            env=env,
            cwd=cwd,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            **kwargs,
        )
    except subprocess.CalledProcessError as err:
        if print_output_on_error or exit_on_error:
            if not verbose:
                _print_info(popenargs, cwd=cwd, kwargs=kwargs)

            human_error(
                message=err.stdout,
                title='Process stdout:',
                exception=err,
            )
        if exit_on_error:
            sys.exit(err.returncode)
        raise
    else:
        return output


class ToolsExecutor:
    """
    Call tools from current Python /.venv/bin/ path.
    """

    def __init__(self, cwd: Path | str | None = None):
        if not cwd:
            cwd = Path.cwd()
        elif not isinstance(cwd, Path):
            cwd = Path(cwd)
        assert_is_dir(cwd)
        self.cwd = cwd

        self.extra_env = {}

        bin_path_str = str(PY_BIN_PATH)
        if bin_path_str not in os.environ['PATH']:
            self.extra_env['PATH'] = bin_path_str + os.pathsep + os.environ['PATH']

        self.extra_env['PYTHONUNBUFFERED'] = '1'

    def _call(self, func: callable, file_name: str, *popenargs, **kwargs):
        bin_path = PY_BIN_PATH / file_name
        assert_is_file(bin_path)

        return func(
            bin_path,
            *popenargs,
            cwd=self.cwd,
            extra_env=self.extra_env,
            **kwargs,
        )

    def is_executable(self, file_name: str) -> bool:
        bin_path = PY_BIN_PATH / file_name
        return bin_path.is_file() and os.access(bin_path, os.X_OK)

    def verbose_check_call(self, file_name: str, *popenargs, **kwargs):
        return self._call(verbose_check_call, file_name, *popenargs, **kwargs)

    def verbose_check_output(self, file_name: str, *popenargs, **kwargs):
        return self._call(verbose_check_output, file_name, *popenargs, **kwargs)
