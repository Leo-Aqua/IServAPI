from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="IServAPI",
    author="Leo Aqua",
    author_email="contact@leoaqua.de",
    description="Unofficial API for IServ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Leo-Aqua/IServAPI",
    keywords=["IServ", "IServAPI", "iserv api", "iserv-api", "API", "Leo-Aqua"],
    py_modules=["IServAPI"],
    use_scm_version={
        "version_scheme": "post-release",
        "local_scheme": "no-local-version",
        "tag_regex": r"v?(?P<version>\d+\.\d+\.\d+)",  # strips the 'v' prefix
    },
    setup_requires=["setuptools_scm"],  # ensures setuptools_scm is available during setup
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
