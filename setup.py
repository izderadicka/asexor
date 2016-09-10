from os.path import os
import re
import sys
import shutil

try:
    from setuptools import setup
    from setuptools.command.install import install
except ImportError:
    from distutils.core import setup
    from distutils.command.install import install
    
pkg_file= os.path.join(os.path.split(__file__)[0], 'asexor', '__init__.py')
cfg_file= os.path.join(os.path.split(__file__)[0], 'xapi-back.cfg.sample')

m=re.search(r"__version__\s*=\s*'([\d.]+)'", open(pkg_file).read())
if not m:
    print >>sys.stderr, 'Cannot find version of package'
    sys.exit(1)

version= m.group(1)


setup(name='asexor',
      version=version,
      description='Asynchronous Executor',
      
      packages=['asexor', ],
      author='Ivan Zderadicka',
      author_email='ivan.zderadicka@gmail.com',
      install_requires=['autobahn>=0.14.1', 'crossbar>=0.14.0'],
      provides=['asexor'],
      keywords=['asyncio', 'tasks scheduler'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Natural Language :: English',
                   'Operating System :: POSIX',
                   'Programming Language :: Python :: 3.5',
                   'Topic :: Communications',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: System :: Distributed Computing']
      
      )