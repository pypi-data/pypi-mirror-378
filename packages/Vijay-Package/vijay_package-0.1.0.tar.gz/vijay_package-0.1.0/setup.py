# setup.py

from setuptools import setup, find_packages

setup(
    name="Vijay_Package",
    version="0.1.0",
    author="Vijay_Kedar",
    author_email="vijaykedar@gmail.com",
    description="A simple printing star toolkit package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prachikabra121/geometry_toolkit",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)