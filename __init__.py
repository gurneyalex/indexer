"""Copyright 2002-2007 Logilab - All Rights Reserved.
"""

def get_indexer(driver, cnx=None, encoding='UTF-8'):
    """
    return the indexer object according to the DB driver
    """
    if driver == 'postgres':
        from indexer.postgres8_indexer import PGIndexer
        return PGIndexer(driver, cnx, encoding)
    elif driver == 'mysql':
        from indexer.mysql_indexer import MyIndexer
        return MyIndexer(driver, cnx, encoding)
    else:
        from indexer.default_indexer import Indexer 
        return Indexer(driver, cnx, encoding)
    
