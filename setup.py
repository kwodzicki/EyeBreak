#!/usr/bin/env python
import os, sys, shutil
from subprocess import Popen
from setuptools import setup, find_packages, convert_path

# Set up app name and other info
NAME    = "EyeBreak"
DESC    = "A GUI program that reminds you to take an eye break"
URL     = "https://github.com/kwodzicki/EyeBreak"
AUTH    = "Kyle R. Wodzicki"
EMAIL   = "krwodzicki@gmail.com"

SCRIPT  = "bin/EyeBreak"
REQUIRE = ["PyQt5"]

if sys.platform == 'darwin': REQUIRE.append( 'pyinstaller' )

main_ns = {}
ver_path = convert_path( os.path.join( NAME, 'version.py' ) )
with open(ver_path, 'r') as ver_file:
  exec( ver_file.read(), main_ns )

def darwin_install():
  topdir = os.path.dirname(os.path.realpath(__file__))
  blddir = "/tmp/2020_build"
  wrkdir = os.path.join( blddir, "work" )
  dstdir = os.path.join( blddir, "dist" )
  icndir = os.path.join( topdir, "icons.iconset" )
  appdir = os.path.join( os.path.expanduser("~"), "Applications" )
  src    = os.path.join( dstdir, "{}.app".format(NAME) )
  dst    = os.path.join( appdir, "{}.app".format(NAME) )
  icon   = os.path.join( blddir, "icons.icns" )
  if not os.path.isdir(wrkdir): os.makedirs( wrkdir )
  if not os.path.isdir(dstdir): os.makedirs( dstdir )
  cmd  = ["iconutil", "-c", "icns", "-o", icon, icndir]
  proc = Popen( cmd )
  proc.communicate( )
  cmd  = ["pyinstaller", "--onefile", "--noconfirm",  "--windowed",
          "--distpath", dstdir,
          "--workpath", wrkdir,
          "--specpath", blddir,
          "--name",     NAME,
          "--icon",     icon,
         SCRIPT]

  proc = Popen( cmd )
  proc.communicate()
  if os.path.isdir( dst ): shutil.rmtree( dst )
  shutil.move( src, appdir )
  shutil.rmtree( blddir )


# Move the app into place in the user's application directory

setup(
  name                 = NAME,
  description          = DESC,
  url                  = URL,
  author               = AUTH,
  author_email         = EMAIL,
  version              = main_ns['__version__'],
  include_package_data = True,
  packages             = find_packages(),
  package_data         = {'' : ['trayicon.jpg']},
  install_requires     = REQUIRE,
  scripts              = [SCRIPT],
  zip_safe             = False,
)

if sys.platform == 'darwin': darwin_install()
