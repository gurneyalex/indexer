""" Copyright Logilab 2002-2003, all rights reserved.

Execute a search in an indexer database

USAGE: %s <query string>
"""

__revision__ = '$Id: search.py,v 1.4 2005-02-25 23:24:29 nico Exp $'

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
    
