#!/usr/bin/env python
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="4channel",
    packages=["fourchannel"],
    version="0.0.2",
    description="A python3 tool and module to download all images/webm from a 4channel thread.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kyle K",
    license="GPLv3",
    author_email="kylek389@gmail.com",
    url="https://github.com/fatalhalt/fourchannel",
    keywords=["4chan", "image", "downloader", "scraper"],
    install_requires=[],
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        "console_scripts": ["4channel=fourchannel.fourchannel:main"],
    },
    python_requires=">=3.6",
)
