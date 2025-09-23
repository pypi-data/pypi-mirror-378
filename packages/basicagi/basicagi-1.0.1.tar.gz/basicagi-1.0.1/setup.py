#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="basicagi",
    version="1.0.0",
    author="Andrius Kairiukstis",
    author_email="k@andrius.mobi",
    description="A Python library for Asterisk Gateway Interface (AGI) applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andrius/asterisk-basicagi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Telecommunications Industry",
        "Topic :: Communications :: Internet Phone",
        "Topic :: Communications :: Telephony",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="asterisk agi pbx telephony voip",
    project_urls={
        "Bug Reports": "https://github.com/andrius/asterisk-basicagi/issues",
        "Source": "https://github.com/andrius/asterisk-basicagi",
        "Documentation": "https://github.com/andrius/asterisk-basicagi/blob/main/README.md",
    },
    include_package_data=True,
    zip_safe=False,
)
