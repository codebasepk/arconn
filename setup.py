from distutils.core import setup
from setuptools import find_packages

setup(
    name='arconn',
    version='1.0',
    description='Turns the light on/off on sun set and rise using Raspberry pi',
    author='CODEBASE PK',
    packages=find_packages(),
    scripts=['main']
)