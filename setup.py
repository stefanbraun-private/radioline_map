#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

cx_freeze setup script for *radioline_map*,
based on help from https://stackoverflow.com/questions/15486292/cx-freeze-doesnt-find-all-dependencies

Copyright (C) 2019 Stefan Braun


This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 2 of the License,
or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see <http://www.gnu.org/licenses/>.
"""



# invoke using:
#  python setup.py build

from cx_Freeze import setup, Executable

import sys
import glob
import os
import zlib
import shutil

# Remove the existing folders folder
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)

########################################
# Here is a list of the Executable options
########################################

#"script":               #the name of the file containing the script which is to be frozen
#"initScript":           #the name of the initialization script that will be executed before the actual script is executed; this script is used to set up the environment for the executable; if a name is given without an absolute path the names of files in the initscripts subdirectory of the cx_Freeze package is searched
#"base":                 #the name of the base executable; if a name is given without an absolute path the names of files in the bases subdirectory of the cx_Freeze package is searched
#"path":                 #list of paths to search for modules
#"targetDir":            #the directory in which to place the target executable and any dependent files
#"targetName":           #the name of the target executable; the default value is the name of the script with the extension exchanged with the extension for the base executable
#"includes":             #list of names of modules to include
#"excludes":             #list of names of modules to exclude
#"packages":             #list of names of packages to include, including all of the package's submodules
#"replacePaths":         #Modify filenames attached to code objects, which appear in tracebacks. Pass a list of 2-tuples containing paths to search for and corresponding replacement values. A search for '*' will match the directory containing the entire package, leaving just the relative path to the module.
#"compress":             #boolean value indicating if the module bytecode should be compressed or not
#"copyDependentFiles":   #boolean value indicating if dependent files should be copied to the target directory or not
#"appendScriptToExe":    #boolean value indicating if the script module should be appended to the executable itself
#"appendScriptToLibrary":#boolean value indicating if the script module should be appended to the shared library zipfile
#"icon":                 #name of icon which should be included in the executable itself on Windows or placed in the target directory for other platforms
#"namespacePackages":    #list of packages to be treated as namespace packages (path is extended using pkgutil)
#"shortcutName":         #the name to give a shortcut for the executable when included in an MSI package
#"shortcutDir":          #the directory in which to place the shortcut when being installed by an MSI package; see the MSI Shortcut table documentation for more information on what values can be placed here.
MY_TARGET_EXE = Executable(
    # what to build
    script = r"radioline_map\generate_map.py",
    initScript = None,
    base = 'Console',
    #targetDir = r"dist",
    targetName = "radioline_map.exe",
    #compress = True,
    #copyDependentFiles = True,
    #appendScriptToExe = False,
    #appendScriptToLibrary = False,
    icon = None
    )

# FIXME: currently I use "cx_Freeze" v5.1.1, and some options are no more available... =>create a clean "setup.py" file!


########################################
#Here is a list of the build_exe options
########################################
#1) append the script module to the executable
append_script_to_exe=False
#2) the name of the base executable to use which, if given as a relative path, will be joined with the bases subdirectory of the cx_Freeze installation; the default value is "Console"
base="Console"
#3) list of names of files to exclude when determining dependencies of binary files that would normally be included; note that version numbers that normally follow the shared object extension are stripped prior to performing the comparison
bin_excludes=[]
#4) list of names of files to include when determining dependencies of binary files that would normally be excluded; note that version numbers that normally follow the shared object extension are stripped prior to performing the comparison
bin_includes=[]
#5) list of paths from which to exclude files when determining dependencies of binary files
bin_path_excludes=[]
#6) list of paths from which to include files when determining dependencies of binary files
bin_path_includes=[]
#7) directory for built executables and dependent files, defaults to build/
build_exe="dist/"
#8) create a compressed zip file
compressed=False
#9) comma separated list of constant values to include in the constants module called BUILD_CONSTANTS in form <name>=<value>
constants=[]
#10) copy all dependent files
copy_dependent_files=True
#11) create a shared zip file called library.zip which will contain all modules shared by all executables which are built
create_shared_zip=True
#12) comma separated list of names of modules to exclude
excludes = []
#13) include the icon in the frozen executables on the Windows platform and alongside the frozen executable on other platforms
icon=False
#13) comma separated list of names of modules to include
includes = []
#15) list containing files to be copied to the target directory;
#  it is expected that this list will contain strings or 2-tuples for the source and destination;
#  the source can be a file or a directory (in which case the tree is copied except for .svn and CVS directories);
#  the target must not be an absolute path
#
# NOTE: INCLUDE FILES MUST BE OF THIS FORM OTHERWISE freezer.py line 128 WILL TRY AND DELETE dist/. AND FAIL!!!
# Here is a list of ALL the DLLs that are included in Python27\Scripts
include_files=[]

# These next DLLs appear to be copied correctly or as needed by cxfreeze...
#           (r"C:\Python27\Scripts\libgcc_s_sjlj-1.dll",           "libgcc_s_sjlj-1.dll"),

#16) include the script module in the shared zip file
include_in_shared_zip=True
#17) include the Microsoft Visual C runtime DLLs and (if necessary) the manifest file required to run the executable without needing the redistributable package installed
include_msvcr =False
#18) the name of the script to use during initialization which, if given as a relative path, will be joined with the initscripts subdirectory of the cx_Freeze installation; the default value is "Console"
init_script=""
#19) comma separated list of packages to be treated as namespace packages (path is extended using pkgutil)
namespace_packages=[]
#20) optimization level, one of 0 (disabled), 1 or 2
optimize=0
#21) comma separated list of packages to include, which includes all submodules in the package
packages = ['asyncio', 'appdirs', 'setuptools', 'packaging', 'numpy', 'idna']
#22) comma separated list of paths to search; the default value is sys.path
path = []
#23) Modify filenames attached to code objects, which appear in tracebacks. Pass a comma separated list of paths in the form <search>=<replace>. The value * in the search portion will match the directory containing the entire package, leaving just the relative path to the module.
replace_paths=[]
#24) suppress all output except warnings
silent=False
#25) list containing files to be included in the zip file directory; it is expected that this list will contain strings or 2-tuples for the source and destination
zip_includes=[]

setup(
    version = "0.0.1",
    description = "radioline_map reads network topology from master RF-module RAD-868-IFS (c) by Phoenix Contact, combines it with GeoJSON metadata and generates an interactive layer on OSM (Open Street Map)",
    author = "Stefan Braun",
    name = "radioline_map",

    options = {"build_exe": {
#                            "append_script_to_exe": append_script_to_exe,
#                            "base":                 base,
                            "bin_excludes":         bin_excludes,
                            "bin_includes":         bin_includes,
                            "bin_path_excludes":    bin_path_excludes,
                            "bin_path_includes":    bin_path_includes,
                            "build_exe":            build_exe,
#                            "compressed":           compressed,
                            "constants":            constants,
#                            "copy_dependent_files": copy_dependent_files,
#                            "create_shared_zip":    create_shared_zip,
                            "excludes":             excludes,
#                            "icon":                 icon,
                            "includes":             includes,
                            "include_files":        include_files,
#                            "include_in_shared_zip":include_in_shared_zip,
                            "include_msvcr":        include_msvcr,
#                            "init_script":          init_script,
                            "namespace_packages":   namespace_packages,
                            "optimize":             optimize,
                            "packages":             packages,
                            "path":                 path,
                            "replace_paths":        replace_paths,
                            "silent":               silent,
                            "zip_includes":         zip_includes,
                             }
               },

    executables = [MY_TARGET_EXE]
    )