"""Indexer for mysql using MyISAM full text search capabilities.

:copyright: 2007-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from os.path import join, dirname, isfile
import glob

from indexer.default_indexer import Indexer, normalize_words
from indexer.query_objects import tokenize

APPEARS_SCHEMA = """
CREATE TABLE appears (
   `uid` integer NOT NULL,
   words text,
   FULLTEXT (words)
) ENGINE = MyISAM;
"""

class MyIndexer(Indexer):
    """Mysql indexer using native functionnalities (FULLTEXT index type of MyISAM tables)

    XXX rely on mysql fti parser / query language
    """

    def cursor_index_object(self, uid, obj, cursor):
        """Index an object, using the db pointed by the given cursor.
        """
        uid = int(uid)
        words = normalize_words(obj.get_words())
        if words:
            cursor.execute("INSERT INTO appears(uid, words) "
                           "VALUES (%(uid)s, %(wrds)s);",
                           {'uid':uid, 'wrds': ' '.join(words)})
        
    def execute(self, querystr, cursor=None):
        """Execute a full text query and return a list of 2-uple (rating, uid).
        """
        if isinstance(querystr, str):
            querystr = unicode(querystr, self.encoding)
        words = normalize_words(tokenize(querystr))
        cursor = cursor or self._cnx.cursor()
        cursor.execute('SELECT 1, uid FROM appears '
                       'WHERE MATCH (words) AGAINST (%(words)s IN BOOLEAN MODE)',
                       {'words': ' '.join(words)})
        return cursor.fetchall()
    
    table = 'appears'
    uid_attr = 'uid'
    need_distinct = False
    
    def restriction_sql(self, tablename, querystr, jointo=None, not_=False):
        """Execute a full text query and return a list of 2-uple (rating, uid).
        """
        if isinstance(querystr, str):
            querystr = unicode(querystr, self.encoding)
        words = normalize_words(tokenize(querystr))
        sql = "MATCH (%s.words) AGAINST ('%s' IN BOOLEAN MODE)" % (tablename, ' '.join(words))
        if not_:
            sql = 'NOT (%s)' % sql
        if jointo is None:
            return sql
        return "%s AND %s.uid=%s" % (sql, tablename, jointo)

    def sql_init_fti(self):
        """Return the sql definition of table()s used by the full text index.
        """
        return APPEARS_SCHEMA

    def sql_drop_fti(self):
        """Drop tables used by the full text index."""
        return 'DROP TABLE appears;'

    def sql_grant_user(self, user):
        return 'GRANT ALL ON appears TO %s;' % (user)
            
