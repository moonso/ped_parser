import codecs
import os
from setuptools import setup, find_packages
import sys

# Shortcut for building/publishing to Pypi
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel upload')
    sys.exit()


setup(
    name="ped_parser",
    version="1.6.5",
    description="A ped file parser.",
    author="Mans Magnusson",
    author_email="mans.magnusson@scilifelab.se",
    url='https://github.com/moonso/ped_parser',
    license='MIT License',
    install_requires=[
        'pytest',
        'click'
    ],
    packages=[
        'ped_parser'
    ],
    scripts=[
        'scripts/ped_parser'
    ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
        "Intended Audience :: Science/Research",
    ],
    long_description = "Parse pedigree files in different formats",
)