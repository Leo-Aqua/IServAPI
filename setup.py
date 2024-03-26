from setuptools import setup, find_packages






with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="IServAPI",
    version="0.2.0",
    author="Leo Aqua",
    author_email="contact@leoaqua.de",
    description="Unofficial API for IServ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Leo-Aqua/IServAPI",
    keywords=["IServ", "IServAPI", "iserv api", "iserv-api", "API", "Leo-Aqua"],
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
        "webdavclient",
        "pandas",
        "html5lib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
