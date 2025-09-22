from setuptools import setup, find_packages

setup(
    name="lalalanigga",  # <-- Make sure this name is unique on PyPI
    version="0.1.1",              # <-- IMPORTANT: Increase the version number
    author="Your Name",
    description="A personal cheatsheet library for my DS practicals.",
    packages=find_packages(),
    package_data={
        "mycheats.practicals": ["*.py"],
    },
    install_requires=[],
)