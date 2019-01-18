#!/usr/bin/env python
from setuptools import setup
import setuptools

setuptools.setup(
  name         = "EyeBreak",
  description  = "A GUI program that reminds you to take an eye break",
  url          = "https://github.com/kwodzicki/makemkv_to_mp4",
  author       = "Kyle R. Wodzicki",
  author_email = "krwodzicki@gmail.com",
  version      = "0.0.1",
  packages     = setuptools.find_packages(),
  install_requires = [ "PyQt5" ],
  scripts=['bin/EyeBreak'],
  zip_save = False,
);
