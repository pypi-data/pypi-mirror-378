
from setuptools import setup, find_packages

setup(
    name="MaxNumberLib",
    version="0.1.0",
    description="Find the maximum number from a list",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mahmmed Albadwy",
    author_email="mamalbadwy23@gmail.com",
    packages=find_packages(),
    python_requires=">=3.13",
    license="MIT",
    entry_points={"console_scripts": ["MaxNumberLib=max_number.__main__:main"]}
)