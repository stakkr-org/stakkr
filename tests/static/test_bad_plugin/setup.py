from setuptools import setup

setup(
    name='StakkrTestPlugin',
    version='3.5',
    packages=['test_plugin'],
    entry_points='''
        [stakkr.plugins]
        test_plugin=test_plugin.core:my_test
    '''
)
