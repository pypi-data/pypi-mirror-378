# -*- coding: utf-8 -*-
"""
This module contains the memhunt tool

"""
from setuptools import setup, find_packages


tests_require = [
    'pytest>=6.0',
    'pytest-cov>=2.10',
    'pytest-mock>=3.0',
]

setup(
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      python_requires='>=3.8',
      install_requires=[
          'setuptools',
          'pympler>=0.9',
          'objgraph>=3.5.0',
          'jinja2>=3.0.0',
      ],
      tests_require=tests_require,
      extras_require={
          'tests': tests_require,
          'fastapi': [
              'fastapi>=0.68.0',
              'uvicorn>=0.15.0',
              'jinja2>=3.0.0',
          ],
          'dev': [
              'pytest>=6.0',
              'pytest-cov>=2.10',
              'pytest-mock>=3.0',
              'fastapi>=0.68.0',
              'uvicorn>=0.15.0',
          ],
      },
      test_suite='memhunt.tests.test_suite',
      )