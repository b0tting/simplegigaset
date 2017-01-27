from setuptools import setup

version = "1.0"

setup(
    name='simplegigaset',
    version=version,
    description='SimpleGigaset: A python wrapper for the Gigaset Elements API',
    author='Mark Otting',
    url='https://github.com/b0tting/simplegigaset',
    license='GNU GPL 2',
    packages=('simplegigaset',),
    install_requires=('requests',),
)