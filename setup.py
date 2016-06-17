# System imports
from sys import path

# Setuptools imports
from setuptools import setup, find_packages

# owls-common imports
path.append('common/modules')
from version_check import owls_python_version_check


# Check that this version of Python is supported
owls_python_version_check()


# Setup owls-cache
setup(
    # Basic installation information
    name = 'owls-cache',
    version = '0.0.2',
    packages = find_packages(exclude = ['common', 'testing']),

    # Dependencies
    install_requires = [
        'six >= 1.7.3',
        'redis >= 2.10.1',
        'nose >= 1.3.3',
    ],

    # Metadata for PyPI
    author = 'Henrik Öhman',
    author_email = 'speeph@gmail.com',
    description = 'Modular analysis toolkit - caching module',
    license = 'MIT',
    keywords = 'python big data analysis',
    url = 'https://github.com/spiiph/owls-cache'
)
