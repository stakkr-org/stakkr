import os


def installed_as_packages():
    if os.path.isdir(os.path.dirname(os.path.realpath(__file__)) + '/static') is True:
        return True

    return False


def get_venv_basedir():
    venv_dir = os.getenv('VIRTUAL_ENV')
    if venv_dir is None:
        raise EnvironmentError("You must be in a virtual environment")

    return os.path.abspath(venv_dir + '/..')


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
