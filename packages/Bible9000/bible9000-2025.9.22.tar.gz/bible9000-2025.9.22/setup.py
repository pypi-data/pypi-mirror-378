# Works, yet beta.toml over-installs the .gsdict files?
#
from __future__ import unicode_literals
from distutils.core import setup
from setuptools import find_packages, find_namespace_packages

# ---from glob import glob as glob
# ---aFiles = glob("Hershey01//GsDict//*.gsdict")
# defer to README.md:
aFiles = [
    "bible9000/biblia.sqlt3",
    ]

zFiles = [
    ('bible9000',aFiles)
    ]

setup(name='bible9000',
      author="Randall Nagy",
      version="1.0.0",
      description="Stick of Joseph: Ancient Wisdom for Our Times.",
      author_email="r.a.nagy@gmail.com",
      url="http://MightyMaxims.com",
      download_url="https://github.com/DoctorQuote/The-Stick-of-Joseph",
      platforms="Cross-Platform CLI / TUI",
      packages=find_namespace_packages(),
      data_files=zFiles)
