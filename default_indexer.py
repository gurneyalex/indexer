# -*- coding: utf-8 -*-
"""Generic Indexer, may be used on any database supporting the Python DB API.

:copyright: 2003-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import re

from logilab.common.adbh import get_adv_func_helper
from logilab.common.textutils import unormalize

from indexer.query import IndexerQuery, IndexerQueryScanner
from indexer.query_objects import Query, tokenize
from indexer._exceptions import StopWord

    
REM_PUNC = re.compile(r"[,.;:!?\n\r\t\)\(«»\<\>/\\\|\[\]{}^#@$£_=+\-*&§]")

SQL_SCHEMA = """

%s

CREATE TABLE word (
  word_id INTEGER PRIMARY KEY NOT NULL,
  word    VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE appears(
  uid     INTEGER,
  word_id INTEGER REFERENCES word ON DELETE CASCADE,
  pos     INTEGER NOT NULL
);

CREATE INDEX appears_uid ON appears (uid);
CREATE INDEX appears_word_id ON appears (word_id);
"""

def normalize(word):
    """Return the normalized form for a word.

    The word given in argument should be unicode !

    currently normalized word are :
       _ in lower case
       _ without any accent

    This function may raise StopWord if the word shouldn't be indexed
    
    stop words are :
       _ single letter
       _ numbers
    """
    assert isinstance(word, unicode), '%r should be unicode' % word
    # do not index single letters
    if len(word) == 1:
        raise StopWord()
    # do not index numbers
    try:
        float(word)
        raise StopWord()
    except ValueError:
        pass
    word = unormalize(word.lower(), ignorenonascii=True)
    return word.encode('ascii', 'ignore')

def normalize_words(rawwords):
    words = []
    for word in rawwords:
        try:
            words.append(normalize(word))
        except StopWord:
            continue
    return words


class Indexer(object):
    """The base indexer.

    Provide an inefficient but generic indexing method which can be overridden.
    """
    table = 'appears'
    uid_attr = 'uid'
    need_distinct = True
    
    def __init__(self, driver, cnx=None, encoding='UTF-8'):
        """cnx : optional Python DB API 2.0 connexion"""
        self.driver = driver
        self._cnx = cnx
        self.encoding = encoding
        self.dbhelper = get_adv_func_helper(driver)

    def has_fti_table(self, cursor):
        return self.table in self.dbhelper.list_tables(cursor)
    
    def index_object(self, uid, obj, cnx=None):
        """ index an object with the given uid
        the object should inherit from or be compatible with Indexable object
        """
        if cnx is None:
            cnx = self._cnx
        cursor = cnx.cursor()
        try:
            self.cursor_index_object(uid, obj, cursor)
            cnx.commit()
        except:
            cnx.rollback()
            raise
            
    def unindex_object(self, uid, cnx=None):
        """ unindex an object
        the object should inherit from or be compatible with Indexable object
        """
        if cnx is None:
            cnx = self._cnx
        cursor = cnx.cursor()
        try:
            self.cursor_unindex_object(uid, cursor)
            cnx.commit()
        except:
            cnx.rollback()
            raise

    def reindex_object(self, uid, obj, cnx=None):
        """ index an object with the given uid
        the object should inherit from or be compatible with Indexable object
        """
        if cnx is None:
            cnx = self._cnx
        cursor = cnx.cursor()
        try:
            self.cursor_reindex_object(uid, obj, cursor)
            cnx.commit()
        except:
            cnx.rollback()
            raise

    def cursor_index_object(self, uid, obj, cursor):
        position = 0
        for word in obj.get_words():
            self._save_word(uid, word, position, cursor)
            position += 1

    def cursor_unindex_object(self, uid, cursor):
        cursor.execute('DELETE FROM appears WHERE uid=%s' % uid)

    def cursor_reindex_object(self, uid, obj, cursor):
        self.cursor_unindex_object(uid, cursor)
        self.cursor_index_object(uid, obj, cursor)
        
    def _save_word(self, uid, word, position, cursor):
        try:
            word = normalize(word)
        except StopWord:
            return
        cursor.execute("SELECT word_id FROM word WHERE word=%(word)s;",
                       {'word':word})
        wid = cursor.fetchone()
        if wid is None:
            wid = self.dbhelper.increment_sequence(cursor, 'word_id_seq')
            try:
                cursor.execute('''INSERT INTO word(word_id, word)
                VALUES (%(uid)s,%(word)s);''', {'uid':wid, 'word':word})
            except:
                # Race condition occured.
                # someone inserted the word before we did.
                # Never mind, let's use the new entry...
                cursor.execute("SELECT word_id FROM word WHERE word=%(word)s;",
                               {'word':word})
                wid = cursor.fetchone()[0]
        else:
            wid = wid[0]
        cursor.execute("INSERT INTO appears(uid, word_id, pos) "
                       "VALUES (%(uid)s,%(wid)s,%(position)s);",
                       {'uid': uid, 'wid': wid, 'position': position})
        
    def execute(self, query_string, cursor=None):
        """execute a full text query and return a list of 2-uple (rating, uid)
        """
        query = Query(normalize)
        parser = IndexerQuery(IndexerQueryScanner(REM_PUNC.sub(' ', query_string)))
        parser.goal(query)
        return query.execute(cursor or self._cnx.cursor())

    def restriction_sql(self, tablename, querystr, jointo=None, not_=False):
        if isinstance(querystr, str):
            querystr = unicode(querystr, self.encoding)
        words = []
        for word in tokenize(querystr):
            try:
                words.append("'%s'" % normalize(word))
            except StopWord:
                continue
        sql = '%s.word_id IN (SELECT word_id FROM word WHERE word in (%s))' % (
            tablename, ', '.join(words))
        if not_:
            sql = 'NOT (%s)' % sql
        if jointo is None:
            return sql
        return '%s AND %s.uid=%s' % (sql, tablename, jointo)

    def init_extensions(self, cursor, owner=None):
        """if necessary, install extensions at database creation time"""
        pass
    
    def sql_init_fti(self):
        """return the sql definition of table()s used by the full text index"""
        return SQL_SCHEMA % self.dbhelper.sql_create_sequence('word_id_seq')

    def sql_drop_fti(self):
        """drop tables used by the full text index"""
        return '''DROP TABLE appears;
DROP TABLE word;'''


    def sql_grant_user(self, user):
        return '''GRANT ALL ON appears_uid TO %s;
GRANT ALL ON appears_word_id TO %s;
GRANT ALL ON appears TO %s;
GRANT ALL ON word TO %s;
''' % (user, user, user, user)
