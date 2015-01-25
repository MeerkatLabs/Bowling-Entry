#!/usr/bin/env python

from distutils.core import setup

setup(name='bowling_entry',
      version='1.0',
      license='',
      description='Bowling Entry core components',
      author='Robert Robinson',
      author_email='rerobins@meerkatlabs.org',
      packages=['bowling_entry', 'bowling_entry.migrations', ],
      package_data={'bowling_entry': ['templates/bowling_entry/*.html']},
      include_package_data=True,
      requires=['django', ],
      )
