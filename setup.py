from setuptools import setup, find_packages

with open("README.md", "r") as stream:
    long_description = stream.read()

setup(
    name = "aminoacids",
    version = "0.1.1",
    description = "Unofficial python wrapper for the Amino web api",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/basswaver/AminoAcids",
    download_url = "https://github.com/basswaver/AminoAcids/tarball/master",
    author = "Zero",
    author_email = "dakoolstwunn@gmail.com",
    licence = "GPLv3",
    classifiers = [
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
    keywords = [
        "amino",
        "amino-bot",
        "bot",
        "reverse-engineering",
        "api",
        "http-api",
        "python",
        "python3",
        "python3.x",
        "unofficial"
    ],
    install_requires = [
        "requests"
    ],
    setup_requires = [
        "wheel"
    ],
    packages = find_packages(),

)
