"""Gives useful information about the current virtualenv, files locations if
stakkr is installed as a package or directly cloned"""


import os

from distutils.sysconfig import get_config_vars, get_python_lib


def get_venv_basedir():
    """Returns the base directory of the virtualenv, useful to read configuration and plugins"""

    try:
        import virtualenv
        raise EnvironmentError("You must be in a virtual environment")
    except Exception:
        return os.path.abspath(get_config_vars()['exec_prefix'] + '/../')


def get_dir(dirname: str):
    """Detects if stakkr is a package or a clone and gives the right path for a directory"""

    staticdir = os.path.dirname(os.path.realpath(__file__)) + '/' + dirname
    if os.path.isdir(staticdir) is True:
        return staticdir

    return get_python_lib() + '/stakkr/' + dirname


def get_file(dirname: str, filename: str):
    """Detects if stakkr is a package or a clone and gives the right path for a file"""

    dir_path = get_dir(dirname)

    return dir_path + '/' + filename.lstrip('/')
