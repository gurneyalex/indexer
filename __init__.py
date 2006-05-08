"""Copyright 2002-2005 Logilab - All Rights Reserved.
"""

__revision__ = '$Id: __init__.py,v 1.17 2006-05-05 10:21:10 david Exp $'

def get_indexer(driver, cnx=None, encoding='UTF-8'):
    """
    return the indexer object according to the DB driver
    """
    if driver == 'postgres7':
        # FIXME: check tsearch is installed ?
        from indexer.postgres_indexer import PGIndexer
        return PGIndexer(cnx, encoding)
    elif driver == 'postgres':
        from indexer.postgres8_indexer import PGIndexer
        return PGIndexer(cnx, encoding)
    else:
        from indexer.default_indexer import Indexer 
        return Indexer(driver, cnx, encoding)

def get_indexer_schema(driver, drop=False):
    """
    return the schema used by the indexer according to the DB driver
    """
    if driver == 'postgres7':
        # FIXME: check tsearch is installed ?
        from indexer.postgres_indexer import get_schema
    elif driver == 'postgres':
        from indexer.postgres8_indexer import get_schema
    else:
        from indexer.default_indexer import get_schema
    return get_schema(driver, drop)


def indexer_definition(driver):
    """return the indexer db specific types/func definition"""
    if driver == 'postgres7':
        # FIXME: check tsearch is installed ?
        from indexer.postgres_indexer import indexer_definition
    elif driver == 'postgres':
        from indexer.postgres8_indexer import indexer_definition
    else:
        from indexer.default_indexer import indexer_definition
    return indexer_definition(driver)
    
def indexer_relation(driver):
    """return the indexer db specific types/func relation"""
    if driver == 'postgres7':
        # FIXME: check tsearch is installed ?
        from indexer.postgres_indexer import indexer_relation
    elif driver == 'postgres':
        from indexer.postgres8_indexer import indexer_relation
    else:
        from indexer.default_indexer import indexer_relation
    return indexer_relation(driver)
    
def indexer_drop_relation(driver):
    """return the indexer db specific types/func relation"""
    if driver == 'postgres7':
        # FIXME: check tsearch is installed ?
        from indexer.postgres_indexer import indexer_drop_relation
    elif driver == 'postgres':
        from indexer.postgres8_indexer import indexer_drop_relation
    else:
        from indexer.default_indexer import indexer_drop_relation
    return indexer_drop_relation(driver)
    
def indexer_grants(driver, user):
    if driver == 'postgres7':
        # FIXME: check tsearch is installed ?
        from indexer.postgres_indexer import indexer_grants
    elif driver == 'postgres':
        from indexer.postgres8_indexer import indexer_grants
    else:
        from indexer.default_indexer import indexer_grants
    return indexer_grants(user)
    
