"""RQL library (implementation independant).

:copyright:
  2001-2008 `LOGILAB S.A. <http://www.logilab.fr>`_ (Paris, FRANCE),
  all rights reserved.

:contact:
  http://www.logilab.org/project/indexer --
  mailto:python-projects@logilab.org

:license:
  `General Public License version 2
  <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>`_
"""
__docformat__ = "restructuredtext en"
from indexer.__pkginfo__ import version as __version__

def get_indexer(driver, cnx=None, encoding='UTF-8'):
    """
    Return the indexer object according to the DB driver.
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
    
