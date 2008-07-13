"""Command to execute a search in an indexer database.

USAGE: %s <query string>

:copyright: 2002-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import sys
import getopt
from os import environ
from logilab.common.db import get_connection
from indexer.default_indexer import Indexer

def help():
    print __doc__ % sys.argv[0]
    sys.exit(0)

# FIXME: use optparse instead of getopt
def run(*args):
    opts, args = getopt.getopt(args, 'd:u:h', ['db-driver=', 'db-uri=', 'help'])
    db_uri = ":indexertest:%s:" % environ['USER']
    driver = 'postgres'
    for opt, val in opts:
        if opt in ('-u', '--db-uri'):
            db_uri = opt
        if opt in ('-d', '--db-driver'):
            driver = opt
        elif opt in ('-h', '--help'):
            help()
            
    if not args:
        help()
    
    cnx = get_connection(driver, *db_uri.split(':'))
    indexer = Indexer(cnx)
    query = ' '.join(args)
    print 'Looking for ', query
    from pprint import pprint
    pprint(indexer.execute(query))


if __name__ == '__main__':
    run(*sys.argv[1:])
    
