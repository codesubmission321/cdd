# Copyright (c) 2016-2020 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

from setuptools import find_packages, setup
from os.path import dirname, join
from setuptools import setup, find_packages
import subprocess

def picire_version():
    with open(join(dirname(__file__), 'picire/VERSION'), 'rb') as f:
        version = f.read().decode('ascii').strip()
    return version

def picire_detailed_version():
    with open(join(dirname(__file__), 'picire/VERSION'), 'rb') as f:
        version = f.read().decode('ascii').strip()
        try:
            git_version = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode('ascii').strip()
            if git_version:
                version = f"{version}+{git_version}"
        except subprocess.CalledProcessError:
            pass
    return version




setup(
    name='picire',
    packages=find_packages(),
    url='https://github.com/renatahodovan/picire',
    license='BSD',
    author='Renata Hodovan, Akos Kiss',
    author_email='hodovan@inf.u-szeged.hu, akiss@inf.u-szeged.hu',
    description='Picire Parallel Delta Debugging Framework',
    long_description=open('README.rst').read(),
    install_requires=['chardet', 'psutil', 'setuptools'],
    zip_safe=False,
    include_package_data=True,
    setup_requires=['setuptools_scm'],
    version=picire_detailed_version(),
    entry_points={
        'console_scripts': ['picire = picire.cli:execute']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Testing',
    ],
)
