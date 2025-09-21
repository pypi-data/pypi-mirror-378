from os import environ
from os import path as os_path
from sys import path as sys_path
from importlib.metadata import version, PackageNotFoundError

from django import setup as django_setup

# pylint: disable=C0415


def init_cli():
    environ.setdefault('AW_INIT', '1')
    # workaround for CI
    if 'AW_VERSION' not in environ:
        try:
            environ['AW_VERSION'] = version('ansible-webui')

        except PackageNotFoundError:
            environ['AW_VERSION'] = '0.0.0'

    try:
        from aw.config.main import init_config

    except ModuleNotFoundError:
        sys_path.append(os_path.dirname(os_path.abspath(__file__)))
        from aw.config.main import init_config

    init_config()

    from aw.config.load_file import load_config_file, check_for_bad_config
    load_config_file()
    check_for_bad_config()

    from aw.utils.debug import warn_if_development
    warn_if_development()

    django_setup()
