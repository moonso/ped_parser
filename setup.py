#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(name="ped_parser",
	version="0.3",
	author="Mans Magnusson",
	author_email="mans.magnusson@scilifelab.se",
    license='BSD',
	description=("A ped file parser."),
	long_description = long_description,
    packages={'ped_parser'},
    url='https://github.com/moonso/ped_parser',
    # scripts=[''],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
        "Intended Audience :: Science/Research",
    ],
)
