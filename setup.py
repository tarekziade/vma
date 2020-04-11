import sys
from setuptools import setup, find_packages


install_requires = []
description = ""

classifiers = [
    "Programming Language :: Python",
    "License :: OSI Approved :: Apache Software License",
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python :: 3 :: Only",
]


setup(
    name="vma",
    version="0.1",
    url="",
    packages=find_packages(),
    long_description=description.strip(),
    description=("Generateur de plans"),
    author="Tarek Ziade",
    author_email="tarek@ziade.org",
    include_package_data=True,
    zip_safe=False,
    classifiers=classifiers,
    install_requires=install_requires,
)
