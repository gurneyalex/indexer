"""
Copyright (c) 2003-2007 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr

indexer packaging information
"""

modname = "indexer"
numversion = (0, 6, 2)
version = '.'.join([str(num) for num in numversion])

license = 'LCL'
copyright = '''Copyright (c) 2003-2007 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Sylvain Thenault"
author_email = "devel@logilab.fr"

short_desc = "a RDBMS full text index library for python"
long_desc = "A library providing an abstraction for full text index in \ndifferent RDBMS, using when possible native capabilites of the DBMS"
web = "" #"http://www.logilab.org/indexer"
#ftp = "ftp://ftp.logilab.org/pub/indexer"

include_dirs = []

# debianize info
debian_maintainer = 'Sylvain Thenault'
debian_maintainer_email = 'sylvain.thenault@logilab.fr'
pyversions = ['2.4']
