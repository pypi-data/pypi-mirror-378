import re

from setuptools import setup


def derive_version() -> str:
    version = ""
    with open("src/game_state/__init__.py") as f:
        version = re.search(
            r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
        )
        if version:
            version = version.group(1)

    if not version:
        raise RuntimeError("Version is not set.")

    return version


setup(version=derive_version())
