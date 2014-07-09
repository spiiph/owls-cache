# System imports
from sys import path

# Setuptools imports
from setuptools import setup

# owls-common imports
path.append('common/modules')
from version_check import owls_python_version_check


# Check that this version of Python is supported
owls_python_version_check()


# Setup owls-cache
setup(
    # Basic installation information
    name = 'owls_cache',
    version = '0.0.1',
    packages = ['owls_cache'],

    # Metadata for PyPI
    author = 'Jacob Howard',
    author_email = 'jacob@havoc.io',
    description = 'Modular analysis toolkit - caching module',
    license = 'MIT',
    keywords = 'python big data analysis',
    url = 'https://github.com/havoc-io/owls-cache'
)
