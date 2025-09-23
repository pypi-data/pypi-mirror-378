"""
    DocWrite: pip_audit.md # Helper to run pip-audit
    https://github.com/pypa/pip-audit
"""

from __future__ import annotations

import logging
from pathlib import Path
import tempfile

from bx_py_utils.pyproject_toml import get_pyproject_config

from cli_base.cli_tools.subprocess_utils import ToolsExecutor


logger = logging.getLogger(__name__)

DEFAULT_OPTIONS = ('--strict', '--require-hashes', '--disable-pip')


def run_pip_audit(base_path: Path | None = None, verbosity: int = 0):
    """DocWrite: pip_audit.md ## cli_base.run_pip_audit.run_pip_audit()
    Call `run_pip_audit()` to run `pip-audit` with configuration from `pyproject.toml`.

    It used `uv export` to generate a temporary `requirements.txt` file
    and pass it to `pip-audit` for checking vulnerabilities.

    pyproject.toml example:

        [tool.cli_base.pip_audit]
        requirements=["requirements.dev.txt"]
        options=["--strict", "--require-hashes", "--disable-pip"]
        ignore-vuln=[
            "CVE-2019-8341", # Jinja2: Side Template Injection (SSTI)
        ]
    """
    tools_executor = ToolsExecutor(cwd=base_path)
    with tempfile.NamedTemporaryFile(prefix='requirements', suffix='.txt') as temp_file:
        tools_executor.verbose_check_call(
            'uv',
            'export',
            '--no-header',
            '--frozen',
            '--no-editable',
            '--no-emit-project',
            '-o',
            temp_file.name,
        )

        config: dict = get_pyproject_config(
            section=('tool', 'cli_base', 'pip_audit'),
            base_path=base_path,
        )
        logger.debug('pip_audit config: %r', config)
        assert isinstance(config, dict), f'Expected a dict: {config=}'

        popenargs = ['pip-audit']

        options = config.get('options', DEFAULT_OPTIONS)
        popenargs.extend(options)

        if verbosity:
            popenargs.append(f'-{"v" * verbosity}')

        for vulnerability_id in config.get('ignore-vuln', []):
            popenargs.extend(['--ignore-vuln', vulnerability_id])

        popenargs.extend(['-r', temp_file.name])

        logger.debug('pip_audit args: %s', popenargs)
        tools_executor.verbose_check_call(*popenargs)
