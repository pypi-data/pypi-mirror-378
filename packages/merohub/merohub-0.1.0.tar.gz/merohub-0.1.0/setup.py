from setuptools import setup, find_packages
import os

setup(
    name="merohub",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else ""
)
