# -*- coding: ISO-8859-1 -*-
"""
Copyright 2003-2005 Logilab -  All Rights Reserved.

Generic Indexer, may be used on ony database supporting the python DB api
"""

__revision__ = '$Id: default_indexer.py,v 1.16 2006-05-05 10:21:11 david Exp $'

import re

from logilab.common.db import get_adv_func_helper

from indexer.query import IndexerQuery, IndexerQueryScanner
from indexer.query_objects import Query, tokenize
from indexer._exceptions import StopWord


NORM_LETTERS = { u'à': 'a', u'ä': 'a', u'â': 'a',
                 u'é': 'e', u'è': 'e', u'ë': 'e', u'ê': 'e',
                 u'ï': 'i', u'î': 'i',
                 u'ö': 'o', u'ô': 'o',
                 u'ù': 'u', u'ü': 'u', u'û': 'u',
                 }

def normalize(word, letters=NORM_LETTERS, encoding='UTF-8'):
    """ Return the normalized form for a word
    The word given in argument should be unicode !

    currently normalized word are :
       _ in lower case
       _ without any accent

    This function may raise StopWord if the word shouldn't be indexed
    
    stop words are :
       _ single letter
       _ numbers
    """
    # do not index single letters
    if len(word) == 1:
        raise StopWord()
    # do not index numbers
    try:
        float(word)
        raise StopWord()
    except ValueError:
        pass
    norm_word = []
    word =  word.lower()
    for char in word:
        norm_word.append(letters.get(char, char))
    result = ''.join(norm_word)
    if isinstance(result, unicode):
        result = result.encode(encoding)
    return result


class Indexer:
    """the base indexer

    provide an inefficient but generic indexing method which can be overridden
    """
    table = 'appears'
    uid_attr = 'uid'
    need_distinct = True
    
    def __init__(self, driver, cnx=None, encoding='UTF-8'):
        """cnx : optional Python DB API 2.0 connexion"""
        self._cnx = cnx
        self.encoding = encoding
        self.adv_func_helper = get_adv_func_helper(driver)

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
            self._save_word(uid, word.lower(), position, cursor)
            position += 1

    def cursor_unindex_object(self, uid, cursor):
        cursor.execute('DELETE FROM appears WHERE uid=%s' % uid)

    def cursor_reindex_object(self, uid, obj, cursor):
        self.cursor_unindex_object(uid, cursor)
        self.cursor_index_object(uid, obj, cursor)
        
    def _save_word(self, uid, word, position, cursor):
        try:
            word = normalize(word, encoding=self.encoding)
        except StopWord:
            return
        cursor.execute("SELECT word_id FROM word WHERE word=%(word)s;",
                       {'word':word})
        wid = cursor.fetchone()
        if wid is None:
            wid = self.adv_func_helper.increment_sequence(cursor, 'word_id_seq')
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


def indexer_definition(driver='postgres'):
    return ''
    

def indexer_relation(driver='postgres'):
    """return the sql definition of the relation used by indexer (require
    definition to be already in)
    """
    helper = get_adv_func_helper(driver)
    schema = SQL_SCHEMA % helper.sql_create_sequence('word_id_seq')
    return schema


def indexer_drop_relation(driver='postgres'):
    """return the sql definition of the relation used by indexer (require
    definition to be already in)
    """
    return '''
DROP TABLE appears;
DROP TABLE word;'''

get_schema = indexer_relation

def indexer_grants(user):
    return '''GRANT ALL ON appears_uid TO %s;
GRANT ALL ON appears_word_id TO %s;
GRANT ALL ON appears TO %s;
GRANT ALL ON word TO %s;
''' % (user, user, user, user)
