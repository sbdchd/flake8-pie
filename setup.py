from typing import Optional

from setuptools import setup


def get_version(fname: str) -> Optional[str]:
    with open(fname) as f:
        for line in f:
            if line.startswith("__version__"):
                raw_version = line.split("=")[-1]
                return raw_version.strip().replace('"', "")
    return None


def get_description(fname: str) -> Optional[str]:
    with open(fname) as f:
        for line in f:
            if line.startswith(">"):
                return line[1:].strip()
    return None


def get_long_description(fname: str) -> str:
    with open(fname, "r") as fh:
        return fh.read()


README = "README.md"

if __name__ == "__main__":
    setup(
        name="flake8-assign-and-return",
        version=get_version("flake8_assign_and_return.py"),
        description=get_description(README),
        long_description=get_long_description(README),
        long_description_content_type="text/markdown",
        license="BSD2 License",
        author="Steve Dignam",
        author_email="steve@dignam.xyz",
        maintainer="Steve Dignam",
        maintainer_email="steve@dignam.xyz",
        url="https://github.com/sbdchd/flake8-assign-and-return",
        classifiers=[
            "Intended Audience :: Developers",
            "Environment :: Console",
            "Programming Language :: Python :: 3.6",
            "Operating System :: OS Independent",
            "License :: OSI Approved :: MIT License",
            "Topic :: Software Development :: Quality Assurance",
        ],
        keywords="flake8, lint",
        entry_points={
            "flake8.extension": ["B = flake8_assign_and_return:AssignAndReturnCheck"]
        },
        install_requires=["flake8"],
        provides=["flake8_assign_and_return"],
        py_modules=["flake8_assign_and_return"],
    )
