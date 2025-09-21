from setuptools import setup, find_packages

"""
find_packages() : scans the current directory and finds all folders 
                  that contain an __init__.py file, treating them as Python packages.
"""

setup(
    name="nativehello",
    version="0.1.0",
    description="A package that says Hello World in various native languages",
    packages=find_packages(),
    install_requires=[],
    keywords="hello world greetings languages",
)
