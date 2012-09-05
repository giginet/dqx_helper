# -*- coding: utf-8 -*-
#
# setup.py
# created by giginet on 2012/09/04
#
#!/usr/bin/env python

from distutils.core import setup

setup(name='dqx_helper',
      version='1.0',
      description='Useful tool collections for DragonQuest X.',
      author='giginet',
      author_email='giginet.net@gmail.com',
      url='http://github.com/giginet/dqx_helper',
      packages=('dqx_helper',),
      requires=('nose', 'pyyaml', 'mechanize', 'BeautifulSoup', 'PIL'),
)
