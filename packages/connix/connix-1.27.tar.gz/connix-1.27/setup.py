from setuptools import setup
import connix

setup(
  name = 'connix',
  packages = ['connix'],
  version = connix.connix.__VERSION__,
  description = 'Connix is a general purpose Python 3.x library that contains a lot of commonly done operations inside of a single package.',
  author = 'Patrick Lambert',
  license = 'MIT',
  author_email = 'patrick@dendory.ca',
  url = 'https://dendory.net',
  download_url = 'https://pypi.org/project/connix/',
  keywords = ['connix', 'util'],
  classifiers = [],
)
