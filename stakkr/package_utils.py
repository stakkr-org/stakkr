"""Gives useful information about the current virtualenv, files locations if
stakkr is installed as a package or directly cloned"""

import os
import sys
from distutils.sysconfig import get_config_vars, get_python_lib


def get_venv_basedir():
    """Returns the base directory of the virtualenv, useful to read configuration and plugins"""

    exec_prefix = get_config_vars()['exec_prefix']
    has_real_prefix = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if has_real_prefix is False or (hasattr(sys, 'real_prefix') and exec_prefix.startswith(sys.real_prefix)):
        raise EnvironmentError('You must be in a virtual environment')

    return os.path.abspath(get_config_vars()['exec_prefix'] + '/../')


def get_dir(dirname: str):
    """Detects if stakkr is a package or a clone and gives the right path for a directory"""

    staticdir = os.path.dirname(os.path.realpath(__file__)) + '/' + dirname
    if os.path.isdir(staticdir) is True:
        return staticdir

    return get_python_lib() + '/stakkr/' + dirname


def get_file(dirname: str, filename: str):
    """Detects if stakkr is a package or a clone and gives the right path for a file"""

    return get_dir(dirname) + '/' + filename.lstrip('/')
