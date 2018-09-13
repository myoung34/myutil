# -*- coding: utf-8 -*-
import codecs
import os.path
import re

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="myutil",
    version=find_version("myutil", "__init__.py"),
    author="Marcus Young",
    author_email="myoung34@my.apsu.edu",
    description=("A demonstration in packaging, testing and general usage by mimicking gcp gsutil."),
    license="MIT",
    keywords="myutil gsutil",
    url="http://github.com/myoung34/myutil",
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': ['myutil=myutil.cli:cli'],
    },
    install_requires=[
        'google-cloud-storage',
        'anytree',
        'click',
    ],

)
