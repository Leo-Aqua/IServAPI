from setuptools import setup, find_packages
import subprocess
import os

remote_verion = subprocess.run(['git', 'describe', '--tags'], stdout=subprocess.PIPE).stdout.decode('utf8').strip()
assert "." in remote_verion


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="IServAPI",
    version=remote_verion,
    author="Leo Aqua",
    author_email="contact@leoaqua.de",
    description="Unofficial API for IServ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Leo-Aqua/IServAPI",
    keywords=["IServ", "IServAPI", "iserv api", "iserv-api", "API", "Leo-Aqua"],
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
        "webdavclient"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
