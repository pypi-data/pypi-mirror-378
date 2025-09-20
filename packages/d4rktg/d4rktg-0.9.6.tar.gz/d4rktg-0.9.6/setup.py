from setuptools import setup, find_packages
from pathlib import Path
import os

VERSION_FILE = "VERSION.txt"

def read_version():
    version_path = Path(VERSION_FILE)
    # If VERSION.txt is missing (e.g. in a source checkout during build),
    # return a sensible default instead of raising so build tools don't fail.
    if not version_path.exists():
        return "0.0.0"
    try:
        version = version_path.read_text(encoding="utf-8").strip()
    except Exception:
        return "0.0.0"
    return version

def get_setup_kwargs(raw: bool = False):
    version = read_version()
    readme = ""
    requirements = []
    try:
        with open('README.rst', encoding='utf-8') as r:
            readme = r.read()
    except Exception:
        # Missing README is non-fatal; leave long_description empty
        readme = ""
    try:
        with open('requirements.txt', encoding='utf-8') as f:
            requirements = f.read().splitlines()
    except Exception:
        # Missing requirements is non-fatal during isolated builds
        requirements = []
    return {
        "name": "d4rktg",
        "version": version,
        "author": "D4rkShell",
        "author_email": "premiumqtrst@gmail.com",
        "packages": find_packages(),
        "install_requires": requirements,
        "keywords": ['python', 'telegram bot', 'D4rkShell'],
        "description": "A module for create with easy and fast",
        "long_description": readme,
        "long_description_content_type": "text/x-rst",
        "classifiers": [
            "Development Status :: 1 - Planning",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
    }

if __name__ == '__main__':
    version = read_version()
    setup(**get_setup_kwargs(raw=False))

