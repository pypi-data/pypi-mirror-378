# setup.py

from setuptools import setup, find_packages

setup(
    name="New_Project_vk",
    version="0.1.3",
    author="Vijay Kedar",
    author_email="vijaykedar96@gmail.com",
    description="A simple math toolkit package",
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
