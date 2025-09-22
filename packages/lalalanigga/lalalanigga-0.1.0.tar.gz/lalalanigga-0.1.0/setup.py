# In file: setup.py
from setuptools import setup, find_packages

setup(
    name="lalalanigga",
    version="0.1.0",
    author="Your Name",
    description="A personal cheatsheet library for my DS practicals.",
    packages=find_packages(),
    package_data={
        "mycheats.practicals": ["*.py"],
    },
    install_requires=[],
)