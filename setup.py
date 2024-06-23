import setuptools


__author__ = "Sobolev Andrey <email.asobolev@gmail.com>"
__version__ = "0.6.0"


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="channel-box",
    version=__version__,
    install_requires=["starlette>=0.37.2", "uvicorn>=0.30.1", "websockets>=12.0"],
    author="Sobolev Andrey",
    url="https://github.com/Sobolev5/channel-box",
    author_email="email.asobolev@gmail.com",
    description="ChannelBox it is a package for Starlette framework that allows you to make named webscoket channels.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(
        exclude=[
            ".git",
            ".gitignore",
            "*.tests",
            "*.tests.*",
            "tests.*",
            "tests",
            "example",
        ]
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
