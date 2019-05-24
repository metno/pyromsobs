# -*- coding: utf-8 -*-

# ------------------------------------
# setup-file for the pyromsobs package
# Ann Kristin Sperrevik, <annksn@met.no>
# MET Norway
# 2017-05-05
# ------------------------------------
from setuptools import setup

setup(name         = 'pyromsobs',
      version      = '0.1',
      description  = 'processing of observations for 4DVAR ROMS in python',
      author       = 'Ann Kristin Sperrevik',
      author_email = 'annks@met.no',
      url          = 'https://github.com/metno/pyromsobs',
      packages     = ['pyromsobs'],
      install_requires=[
        'roppy==0.6',
        'numpy>=1.16,<2.0',
        'scipy>=1.2,<2.0',
        'netcdf4>=1.4,<2.0',
        'matplotlib>=3.0,<4.0',
        'pyproj>=1.9,<3.0'
      ],
      dependency_links = ['pip install git+https://github.com/bjornaa/roppy.git --process-dependency-links --allow-all-external']
      )
