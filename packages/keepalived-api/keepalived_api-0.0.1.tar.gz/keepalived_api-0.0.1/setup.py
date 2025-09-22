import os
import sys
from setuptools import setup, find_packages

PACKAGE_NAME = "keepalived-api"
VERSION = "0.0.1"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def fread(file) -> str:
    # First try the standard path
    file_path = os.path.join(ROOT_DIR, file)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    
    # For sdist builds, try relative path
    if os.path.exists(file):
        with open(file, "r") as f:
            return f.read()
            
    # If we can't find the file, return empty string
    return ""


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    long_description=fread("README.md").strip(),
    long_description_content_type="text/markdown",
    author="charnet1019",
    url="https://github.com/charnet1019/keepalived-api",
    license="GPL-3.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)