import os
import sys


def installed_as_packages():
    if os.path.isdir(os.path.dirname(os.path.realpath(__file__)) + '/static') is True:
        return True

    return False


def get_venv_basedir():

    if not hasattr(sys, 'real_prefix'):
        raise EnvironmentError("You must be in a virtual environment")

    return os.path.abspath(sys.base_prefix + '/..')


def get_static_file(filename: str):
    staticdir = get_static_dir()
    if staticdir is not True:
        return staticdir + '/' + filename.lstrip('/')


def get_static_dir():
    staticdir = os.path.dirname(os.path.realpath(__file__)) + '/static'
    if os.path.isdir(staticdir) is True:
        return staticdir

    from distutils.sysconfig import get_python_lib

    return get_python_lib() + '/marina'


def get_distinfo_dir():
    if installed_as_packages() is False:
        raise Exception('You can get the distinfo dir only if you installed marina as a package')

    from distutils.sysconfig import get_python_lib
    return get_python_lib()
