#!/usr/bin/env python
# pylint: disable-msg=W0404
"""Generic Setup script, takes package info from __pkginfo__.py file.

:copyright: 2003-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import os
import sys
import shutil
from os.path import isdir, exists, join, walk
from distutils.core import setup
from distutils.command import install_lib

# import required features
from __pkginfo__ import modname, version, license, short_desc, long_desc, \
     web, author, author_email
# import optional features
try:
    from __pkginfo__ import scripts
except ImportError:
    scripts = []
try:
    from __pkginfo__ import data_files
except ImportError:
    data_files = None
try:
    from __pkginfo__ import subpackage_of
except ImportError:
    subpackage_of = None
try:
    from __pkginfo__ import include_dirs
except ImportError:
    include_dirs = []
try:
    from __pkginfo__ import ext_modules
except ImportError:
    ext_modules = None

BASE_BLACKLIST = ('CVS', 'debian', 'dist', 'build', '__buildlog')
IGNORED_EXTENSIONS = ('.pyc', '.pyo', '.elc')
    

def ensure_scripts(linuxScripts):
    """
    Creates the proper script names required for each platform
    (taken from 4Suite)
    """
    from distutils import util
    _scripts = linuxScripts
    if util.get_platform()[:3] == 'win':
        _scripts = [script + '.bat' for script in _scripts]
    return _scripts


def get_packages(directory, prefix):
    """return a list of subpackages for the given directory
    """
    result = []
    for package in os.listdir(directory):
        absfile = join(directory, package)
        if isdir(absfile):
            if exists(join(absfile, '__init__.py')) or \
                   package in ('test', 'tests'):
                if prefix:
                    result.append('%s.%s' % (prefix, package))
                else:
                    result.append(package)
                result += get_packages(absfile, result[-1])
    return result

def export(from_dir, to_dir,
           blacklist=BASE_BLACKLIST,
           ignore_ext=IGNORED_EXTENSIONS):
    """make a mirror of from_dir in to_dir, omitting directories and files
    listed in the black list
    """
    if isdir(from_dir):
        def make_mirror(arg, directory, fnames):
            """walk handler"""
            for norecurs in blacklist:
                try:
                    fnames.remove(norecurs)
                except ValueError:
                    pass
            for filename in fnames:
                # don't include binary files
                if filename[-4:] in ignore_ext:
                    continue
                if filename[-1] == '~':
                    continue
                src = '%s/%s' % (directory, filename)
                dest = to_dir + src[len(from_dir):]
                print >> sys.stderr, src, '->', dest
                if os.path.isdir(src):
                    if not exists(dest):
                        os.mkdir(dest)
                else:
                    if exists(dest):
                        os.remove(dest)
                    shutil.copy2(src, dest)
        try:
            os.mkdir(to_dir)
        except OSError, ex:
            # file exists ?
            import errno
            if ex.errno != errno.EEXIST:
                raise
        walk(from_dir, make_mirror, None)
    else:
        try:
            shutil.copy2(from_dir, to_dir)
        except OSError, ex:
            # file exists ?
            import errno
            if ex.errno != errno.EEXIST:
                raise
        


class InstallLib(install_lib.install_lib):
    """extends distutils install_lib command to create the main package __init__
    and to optionaly include additional data in the subpackage directory
    """

    def run(self):
        install_lib.install_lib.run(self)
        # manually install included directories if any
        base = modname
        for directory in include_dirs:
            dest = join(self.install_dir, base, directory)
            export(directory, dest)

def install(**kwargs):
    """setup entry point"""
    kwargs['package_dir'] = {modname : '.'}
    kwargs['packages'] = [modname] + get_packages(os.getcwd(), modname)
    return setup(name = modname,
                 version = version,
                 license =license,
                 description = short_desc,
                 long_description = long_desc,
                 author = author,
                 author_email = author_email,
                 url = web,
                 scripts = ensure_scripts(scripts),
                 data_files=data_files,
                 ext_modules=ext_modules,
                 cmdclass={'install_lib': InstallLib},
                 **kwargs)
            
if __name__ == '__main__' :
    install()
