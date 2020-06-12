import os
import sys
import setuptools

__author__ = 'Sobolev Andrey <email.asobolev@gmail.com>'
__version__ = '0.1.5'

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='channel-box',
    version=__version__,
    install_requires=['simple_print>=0.2', 'starlette>=0.13.4'],
    author='Sobolev Andrey',
    url="https://github.com/Sobolev5/channel-box",        
    author_email='email.asobolev@gmail.com',
    description='ChannelBox is a convenient tool for Starlette framework that allows you send messages to groups of channels.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)