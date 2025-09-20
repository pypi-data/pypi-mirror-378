
from setuptools import setup, find_packages

setup(
    name="StringUtilsLib",
    version="0.1.0",
    description="Text utilities: reverse, count letters and words",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Raghed Ehap Suif Alfaghe",
    author_email="raralasaly2006@gmail.com",
    packages=find_packages(),
    python_requires=">=3.13",
    license="MIT",
    entry_points={"console_scripts": ["StringUtilsLib=string_utils.__main__:main"]}
)
