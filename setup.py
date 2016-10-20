import codecs
import os
import re
from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

setup(
    name='rangetree',
    version='1.0',
    py_modules=['rangetree'],
    url='https://github.com/nanobit/rangetree',
    license='Apache 2.0',
    author='Tin Tvrtkovic',
    author_email='tin.tvrtkovic@nanobit.co',
    description='Quick lookups of values in numeric ranges.',
    long_description=readme,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.5",
    ],
    install_requires=[
        'bintrees',
    ],
)
