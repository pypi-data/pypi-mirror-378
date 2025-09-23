# Legacy shim for old tooling (`pip install .` still works)
# Modern builds use pyproject.toml (PEP 517/518).
from setuptools import setup
setup()
