import setuptools


__author__ = "Sobolev Andrey <email.asobolev@gmail.com>"
__version__ = "0.5.1.6"


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="channel-box",
    version=__version__,
    install_requires=["starlette>=0.20.4", "uvicorn[standart]>=0.18.3"],
    author="Sobolev Andrey",
    url="https://github.com/Sobolev5/channel-box",        
    author_email="email.asobolev@gmail.com",
    description="ChannelBox it is a package for Starlette framework that allows you to make named webscoket channels.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=[".git", ".gitignore", "*.tests", "*.tests.*", "tests.*", "tests", "example"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)