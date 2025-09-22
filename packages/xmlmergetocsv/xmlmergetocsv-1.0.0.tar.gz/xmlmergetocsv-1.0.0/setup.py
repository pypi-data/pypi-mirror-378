from setuptools import setup, find_packages

#with open("readme.md", "r", encoding="utf-8") as fh:
#    long_description = fh.read()

setup(
    name="xmlmergetocsv",
    version="1.0.0",
    author="Me",
    author_email="",
    description="A Python package to merge XML data to CSV format File",
    long_description="long_description",
    long_description_content_type="text/markdown",
    url="https://",
    package_dir={"": "xml2csv"},
    packages=find_packages(where="xml2csv"),
    install_requires=[
        "pandas",
        "ElementTree",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
     #   "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)