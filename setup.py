from setuptools import setup
import subprocess

def get_version():
    try:
        version = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.DEVNULL).decode().strip().lstrip("v")
        print("Detected version from git tags:", version)
        return version
    except Exception as e:
        print("Could not get version from git tags, using fallback. Error:", e)
        return "0.1.1"  # fallback to existing version to prevent uploading it to pypi

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="IServAPI",
    version=get_version(),
    author="Leo Aqua",
    author_email="contact@leoaqua.de",
    description="Unofficial API for IServ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Leo-Aqua/IServAPI",
    keywords=["IServ", "IServAPI", "iserv api", "iserv-api", "API", "Leo-Aqua"],
    py_modules=["IServAPI"],
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
        "webdavclient",
        "pandas",
        "html5lib",
        "python-dateutil",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
