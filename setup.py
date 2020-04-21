#  Copyright (c) 2020. Stephen R. Ouellette

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='CoronaVirusChatBot',
    version='1.0.0',
    packages=find_packages(where='src'),
    url='',
    license='',
    author='Stephen R Ouellette',
    author_email='Stephen.r.ouellette@gmail.com',
    description='COVID-19 Virus chat bot',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Instructors',
        'Topic :: Artificial Intelligence :: COVID-19',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',

)
