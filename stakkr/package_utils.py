"""Gives useful information about the current virtualenv, files locations if
marina is installed as a package or directly cloned"""


import os

from distutils.sysconfig import get_python_lib


def installed_as_packages():
    """True if marina is installed as a package, else False"""

    if os.path.isdir(os.path.dirname(os.path.realpath(__file__)) + '/static') is True:
        return True

    return False


def get_venv_basedir():
    """Returns the base directory of the virtualenv, useful to read configuration and plugins"""

    try:
        import virtualenv
        raise EnvironmentError("You must be in a virtual environment")
    except Exception:
        return os.path.abspath(get_python_lib() + '/../../../../')


def get_file(dirname: str, filename: str):
    """Detects if marina is a package or a clone and gives the right path for a file"""

    dir_path = get_dir(dirname)

    return dir_path + '/' + filename.lstrip('/')


def get_dir(dirname: str):
    """Detects if marina is a package or a clone and gives the right path for a directory"""

    staticdir = os.path.dirname(os.path.realpath(__file__)) + '/' + dirname
    if os.path.isdir(staticdir) is True:
        return staticdir


    return get_python_lib() + '/marina/' + dirname
