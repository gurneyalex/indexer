"""
Copyright 2003-2006 Logilab - All Rights Reserved.

Indexer for postgres using tsearch  from the openfts project
(http://openfts.sourceforge.net/)

Warning: you will need to run the script with db super user priviledges. 
"""

from os.path import join, dirname, isfile
import glob

from indexer.default_indexer import Indexer, normalize
from indexer._exceptions import StopWord
from indexer.query_objects import tokenize


class PGIndexer(Indexer):
    """postgresql indexer using native functionnalities (tsearch)
    """
    

    def cursor_index_object(self, uid, obj, cursor):
        """index an object, using the db pointed by the given cursor
        """
        uid = int(uid)
        words = []
        for word in obj.get_words():
            try:
                words.append(normalize(word))
            except StopWord:
                continue
        if words:
            cursor.execute("INSERT INTO appears(uid, words) "
                           "VALUES (%(uid)s,%(wrds)s);",
                           {'uid':uid, 'wrds': ' '.join(words)})
        
    def execute(self, query_string, cursor=None):
        """execute a full text query and return a list of 2-uple (rating, uid)
        """
        if isinstance(query_string, str):
            query_string = unicode(query_string, self.encoding)
        words = []
        for word in tokenize(query_string):
            try:
                words.append(normalize(word))
            except StopWord:
                continue
        attrs = {'words': '&'.join(words)}
        cursor = cursor or self._cnx.cursor()
        cursor.execute('SELECT 1, uid FROM appears '
                       "WHERE words @@ '%(words)s'" % attrs)
        return cursor.fetchall()
    
    table = 'appears'
    uid_attr = 'uid'
    need_distinct = False
    
    def restriction_sql(self, tablename, querystr, jointo=None, not_=False):
        """execute a full text query and return a list of 2-uple (rating, uid)
        """
        if isinstance(querystr, str):
            querystr = unicode(querystr, self.encoding)
        words = []
        for word in tokenize(querystr):
            try:
                words.append(normalize(word))
            except StopWord:
                continue
        sql = "%s.words @@ '%s'" % (tablename, '&'.join(words))
        if not_:
            sql = 'NOT (%s)' % sql
        if jointo is None:
            return sql
        return "%s AND %s.uid=%s" % (sql, tablename, jointo)


TSEARCH_SCHEMA_PATH = ('/usr/lib/postgresql/share/contrib/tsearch.sql',
                       '/usr/share/postgresql/contrib/tsearch.sql',
                       '/usr/lib/postgresql-?.?/share/contrib/tsearch.sql',
                       '/usr/share/postgresql-?.?/contrib/tsearch.sql',
                       '/usr/share/postgresql/?.?/contrib/tsearch.sql',
                       join(dirname(__file__), 'tsearch.sql'),
                       'tsearch.sql')
APPEARS_SCHEMA = """
%s

CREATE table APPEARS(
  uid     INTEGER PRIMARY KEY NOT NULL,
  words   txtidx
);

CREATE INDEX appears_uid ON appears (uid);
"""


def get_schema(driver='postgres', drop=False):
    """return the tsearch schema and indexer's additional schema
    """
    assert driver == 'postgres', driver
    return indexer_definition() + '\n' + indexer_relation(drop=drop)


def indexer_definition(driver='postgres'):
    """return the tsearch types/func definition"""
    assert driver == 'postgres', driver
    for path in TSEARCH_SCHEMA_PATH:
        for fullpath in glob.glob(path):
            if isfile(fullpath):
                return open(fullpath).read()
    raise Exception('tsearch.sql not found')

def indexer_relation(driver='postgres', drop=False):
    """return the sql definition of the relation used by indexer (require
    definition to be already in)
    """
    assert driver == 'postgres', driver
    my_schema = APPEARS_SCHEMA
    if drop:
        my_schema %= '''DROP INDEX appears_uid;
DROP TABLE appears;'''
    else:
        my_schema %= ''
    return my_schema

def indexer_grants(user):
    return '''GRANT ALL ON appears TO %s;
''' % (user)
