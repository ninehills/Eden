from setuptools import setup, find_packages
import sys
from eden import __version__

setup(
    name = 'Eden',
    version = __version__,
    author = "Thomas Huang",
    author_email='lyanghwy@gmail.com',
    description = "A Python Distributed Task System",
    license = "GPL",
    keywords = "Python Distributed Task System",
    url='https://github.com/thomashuang/Eden',
    long_description=open('README.md').read(),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires = ['setuptools'],
    classifiers=(
        "Development Status :: Production/Alpha",
        "License :: GPL",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: RSS"
        )
    )