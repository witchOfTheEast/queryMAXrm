#! /bin/python

# setup script for queryMAXrm.py

from setuptools import setup

setup(
    author='Randall Dunn',
    author_email='justThisGuyRandall@gmail.com',
    name='queryMAXrm',
    packages=['queryMAXrm'],
    version='0.1',
    install_requires=['BeautifulSoup4', 'datetime', 'lxml', 'requests', 'ConfigParser', 'reportlab', 'html5lib'],
    long_description=open('README.txt').read()
    )
