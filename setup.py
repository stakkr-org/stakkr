import os
from setuptools import setup


extra_packages = []
if os.name == 'nt':
    extra_packages.append('pypiwin32')

__version__ = '4.1.7'

# Get the long description from the README file
def readme():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
        return f.read()

setup(
    name='stakkr',
    version=__version__,
    description='A configurable stack based on docker to run any combination of services (PHP, MySQL, Apache, Nginx, Mongo, etc..)',
    long_description=readme(),
    url='http://github.com/stakkr-org/stakkr',
    author='Emmanuel Dyan',
    author_email='emmanueldyan@gmail.com',
    license='Apache 2.0',
    packages=['stakkr'],
    py_modules=['stakkr'],
    python_requires='>=3.3',
    entry_points='''[console_scripts]
stakkr=stakkr.cli:main
stakkr-init=stakkr.setup:init
stakkr-compose=stakkr.stakkr_compose:cli''',
    include_package_data=True,
    install_requires=[
        'docker-compose>1.20<1.30',
        'click-plugins==1.1.1',
        'clint==0.5.1',
        'anyconfig==0.9',
        'humanfriendly==4.18',
        'GitPython==2.1.11'
        ] + extra_packages,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration',
    ],
    keywords='docker,docker-compose,python,stack,development,lamp,vagrant',
)
