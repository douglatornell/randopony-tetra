import os
from setuptools import setup, find_packages
import __pkg_metadata__

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'celery',
    'colander==1.2',
    'deform==0.9.9',
    # 'gdata',
    'pyramid',
    'pyramid-crow',
    'pyramid-debugtoolbar',
    'pyramid-deform',
    'pyramid-mailer',
    'pyramid-mako',
    'pyramid-tm',
    'pytz',
    'SQLAlchemy',
    'stormpath',
    # 'supervisor',
    'transaction',
    'waitress',
    'zope.sqlalchemy',
]

setup(name='RandoPony',
      version=__pkg_metadata__.number + __pkg_metadata__.release,
      description='RandoPony',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Development Status :: " + __pkg_metadata__.dev_status,
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Doug Latornell',
      author_email='djl@douglatornell.ca',
      url='http://randopony.randonneurs.bc.ca',
      keywords='web wsgi bfg pylons pyramid cycling randonnee',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='randopony',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = randopony:main
      [console_scripts]
      initialize_RandoPony_db = randopony.scripts.initializedb:main
      """,
      )
