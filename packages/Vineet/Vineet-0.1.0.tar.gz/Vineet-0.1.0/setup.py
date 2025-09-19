# setup.py

from setuptools import setup, find_packages

setup(
    name="Vineet",
    version="0.1.0",
    author="K Dinkar",
    author_email="vineetkotari98@gmail.com",
    description="Sample Package Printing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vineet12kotari/dinkar_package",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)