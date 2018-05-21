import os
from distutils.core import setup
from stakkr.setup import StakkrPostInstall


here = os.path.abspath(os.path.dirname(__file__))
extra_packages = []
if os.name == 'nt':
    extra_packages.append('pypiwin32')


__version__ = '3.6.4'

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stakkr',
    version=__version__,
    description='A configurable stack based on docker to run any combination of services (PHP, MySQL, Apache, Nginx, Mongo, etc..)',
    long_description=long_description,
    url='http://github.com/edyan/stakkr',
    author='Emmanuel Dyan',
    author_email='emmanueldyan@gmail.com',
    license='Apache 2.0',
    packages=['stakkr'],
    py_modules=['stakkr'],
    entry_points='''[console_scripts]
docker-clean=stakkr.docker_clean:main
stakkr=stakkr.cli:main
stakkr-init=stakkr.setup:init
stakkr-compose=stakkr.stakkr_compose:cli''',
    include_package_data=True,
    install_requires=[
        'click-plugins==1.0.3',
        'clint==0.5.1',
        'configobj==5.0.6',
        # Docker compose includes requests and docker
        'docker-compose<1.20.0'
        ] + extra_packages,
    cmdclass={'install': StakkrPostInstall},
    classifiers=[
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration',
    ],
    keywords='docker,docker-compose,python,stack,development,lamp,vagrant',
)
