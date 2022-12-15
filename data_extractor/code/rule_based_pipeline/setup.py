import io
import os
from pathlib import Path

from setuptools import find_packages, setup

NAME = 'rule_based_pipeline'
DESCRIPTION = 'Run rule-based solution'
AUTHOR = 'I. Demir'
REQUIRES_PYTHON = '>=3.6.0'

def list_reqs(fname='requirements.txt'):
    with open(fname) as fd:
        return fd.read().splitlines()

here = os.path.abspath(os.path.dirname(__file__))

# Load the package's __version__.py module as a dictionary.
ROOT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = ROOT_DIR / NAME
about = {}
with open(PACKAGE_DIR / 'VERSION') as f:
    _version = f.read().strip()
    about['__version__'] = _version

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    author=AUTHOR,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(),
    package_data={'rule_based_pipeline': ['VERSION']},
    install_requires=list_reqs(),
    extras_require={},
    include_package_data=True
)
