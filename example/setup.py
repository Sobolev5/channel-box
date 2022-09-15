import os
import sys
import setuptools

__author__ = "Sobolev Andrey <email.asobolev@gmail.com>"
__version__ = "0.4.0"


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="channel-box",
    version=__version__,
    install_requires=["starlette>=0.20.4", "shortuuid>=1.0.9", "uvicorn[standart]>=0.18.3"],
    author="Sobolev Andrey",
    url="https://github.com/Sobolev5/channel-box",        
    author_email="email.asobolev@gmail.com",
    description="channel-box it is a simple tool for Starlette framework that allows you to make named webscoket channels.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=[".git", ".gitignore"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)