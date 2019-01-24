#!/usr/bin/env python
import os, sys, shutil;
from subprocess import Popen;
from setuptools import setup;
import setuptools;

# Set up app name and other info
name    = "20-20-20 EyeBreak";
script  = "bin/EyeBreak";
require = ["PyQt5"]
if sys.platform == 'darwin': require.append( 'pyinstaller' );

def darwin_install():
  topdir = os.path.dirname(os.path.realpath(__file__));
  blddir = "/tmp/2020_build";
  wrkdir = os.path.join( blddir, "work" );
  dstdir = os.path.join( blddir, "dist" );
  icndir = os.path.join( topdir, "icons.iconset" );
  appdir = os.path.join( os.path.expanduser("~"), "Applications" );
  src    = os.path.join( dstdir, "{}.app".format(name) );
  dst    = os.path.join( appdir, "{}.app".format(name) );
  icon   = os.path.join( blddir, "icons.icns" );
  if not os.path.isdir(wrkdir): os.makedirs( wrkdir );
  if not os.path.isdir(dstdir): os.makedirs( dstdir );
  cmd  = ["iconutil", "-c", "icns", "-o", icon, icndir];
  proc = Popen( cmd );
  proc.communicate( )
  cmd  = ["pyinstaller", "-ywF",
          "--distpath", dstdir,
          "--workpath", wrkdir,
          "--specpath", blddir,
          "--name",     name,
          "-i",         icon,
         script]
  proc = Popen( cmd );
  proc.communicate();
  if os.path.isdir( dst ): shutil.rmtree( dst );
  shutil.move( src, appdir );
  shutil.rmtree( blddir );


# Move the app into place in the user's application directory

setuptools.setup(
  name             = name,
  description      = "A GUI program that reminds you to take an eye break",
  url              = "https://github.com/kwodzicki/EyeBreak",
  author           = "Kyle R. Wodzicki",
  author_email     = "krwodzicki@gmail.com",
  version          = "0.0.3",
  packages         = setuptools.find_packages(),
  install_requires = require,
  scripts          = [script],
  zip_save         = False,
);

if sys.platform == 'darwin': darwin_install();