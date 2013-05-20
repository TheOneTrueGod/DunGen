# py2exe setup program
from distutils.core import setup
import py2exe
import sys
import os
import glob, shutil, pygame
sys.argv.append("py2exe")
 
 
def getDataFiles(mainDir, currDir):
	toRet = []
	numDirs = len(os.listdir(mainDir))
	for dir in os.listdir(mainDir):
		if os.path.isdir(os.path.join(mainDir, dir)):
			numDirs -= 1
			toRet += getDataFiles(os.path.join(mainDir, dir), dir)
	if numDirs > 0:
		toRet += [(mainDir, glob.glob(os.path.join(mainDir, "*.*")))]
	return toRet
	
VERSION = '0.6'
AUTHOR_NAME = 'Jeremy Prevoe'
AUTHOR_EMAIL = 'jprevoe@gmail.com'
PRODUCT_NAME = "Zombies"
SCRIPT_MAIN = 'Game.py'
VERSIONSTRING = PRODUCT_NAME + " ALPHA " + VERSION
ICONFILE = "icon.ico"
 
# Remove the build tree on exit automatically
REMOVE_BUILD_ON_EXIT = True
PYGAMEDIR = os.path.split(pygame.base.__file__)[0]
 
SDL_DLLS = glob.glob(os.path.join(PYGAMEDIR,'*.dll'))
 
if os.path.exists('dist/'): shutil.rmtree('dist/')
 
extra_files = getDataFiles("Data", "Data")
 
# List of all modules to automatically exclude from distribution build
# This gets rid of extra modules that aren't necessary for proper functioning of app
# You should only put things in this list if you know exactly what you DON'T need
# This has the benefit of drastically reducing the size of your dist
 
INCLUDE_STUFF = ['encodings',"encodings.latin_1",]
 
setup(windows=[
             {'script': SCRIPT_MAIN,
               'other_resources': [(u"VERSIONTAG",1,VERSIONSTRING)],
               'icon_resources': [(1,ICONFILE)]}],
         options = {"py2exe": {
                             "optimize": 2,
                             "includes": INCLUDE_STUFF,
                             "compressed": 1,
                             "ascii": 1,
                             "bundle_files": 2,
                             "ignores": ['tcl','AppKit','Numeric','Foundation']} },
          name = PRODUCT_NAME,
          version = VERSION,
          data_files = extra_files,
          zipfile = None,
          author = AUTHOR_NAME,
          author_email = AUTHOR_EMAIL)
 
# Create the /save folder for inclusion with the installer
shutil.copytree('Profiles','dist/Profiles')
#shutil.copytree('help','dist/help')
 
for f in SDL_DLLS:
    fname = os.path.basename(f)
    try:
        shutil.copyfile(f,os.path.join('dist',fname))
    except: pass
 
if os.path.exists('dist/tcl'): shutil.rmtree('dist/tcl') 
 
if os.path.exists('dist/tcl84.dll'): os.unlink('dist/tcl84.dll')
if os.path.exists('dist/tk84.dll'): os.unlink('dist/tk84.dll')

# Remove the build tree
if REMOVE_BUILD_ON_EXIT:
     shutil.rmtree('build/')