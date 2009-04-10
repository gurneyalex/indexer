"""Indexer for Postgresql using tsearch2 from the openfts project
(see http://openfts.sourceforge.net/)

Warning: you will need to run the tsearch2.sql script with super user privileges
on the database.

:copyright: 2005-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from os.path import join, dirname, isfile
import glob

from indexer.default_indexer import Indexer, normalize_words
from indexer.query_objects import tokenize



TSEARCH_SCHEMA_PATH = ('/usr/share/postgresql/?.?/contrib/tsearch2.sql', # current debian 
                       '/usr/lib/postgresql/share/contrib/tsearch2.sql',
                       '/usr/share/postgresql/contrib/tsearch2.sql',
                       '/usr/lib/postgresql-?.?/share/contrib/tsearch2.sql',
                       '/usr/share/postgresql-?.?/contrib/tsearch2.sql',
                       join(dirname(__file__), 'tsearch2.sql'),
                       'tsearch2.sql')
APPEARS_SCHEMA = """
CREATE table appears(
  uid     INTEGER PRIMARY KEY NOT NULL,
  words   tsvector
);
"""

class PGIndexer(Indexer):
    """Postgresql indexer using native functionnalities (tsearch2).
    """
    config = 'default'
    
    def has_fti_table(self, cursor):
        if super(PGIndexer, self).has_fti_table(cursor):
            cursor.execute('SELECT version()')
            version = cursor.fetchone()[0].split()[1]
            version = [int(i) for i in version.split('.')]
            if version >= [8, 3, 0]:
                self.config = 'simple'
            else:
                self.config = 'default'
        return self.table in self.dbhelper.list_tables(cursor)
    

    def cursor_index_object(self, uid, obj, cursor):
        """Index an object, using the db pointed by the given cursor.
        """
        uid = int(uid)
        words = normalize_words(obj.get_words())
        if words:
            cursor.execute("INSERT INTO appears(uid, words) "
                           "VALUES (%(uid)s,to_tsvector(%(config)s, %(wrds)s));",
                           {'config': self.config, 'uid':uid, 'wrds': ' '.join(words)})
        
    def execute(self, querystr, cursor=None):
        """Execute a full text query and return a list of 2-uple (rating, uid).
        """
        if isinstance(querystr, str):
            querystr = unicode(querystr, self.encoding)
        words = normalize_words(tokenize(querystr))
        cursor = cursor or self._cnx.cursor()
        cursor.execute('SELECT 1, uid FROM appears '
                       "WHERE words @@ to_tsquery(%(config)s, %(words)s)",
                       {'config': self.config, 'words': '&'.join(words)})
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
        # XXX replace '%' since it makes tsearch fail, dunno why yet, should
        # be properly fixed
        searched = '&'.join(words).replace('%', '')
        sql = "%s.words @@ to_tsquery('%s', '%s')" % (tablename, self.config, searched)
        if not_:
            sql = 'NOT (%s)' % sql
        if jointo is None:
            return sql
        return "%s AND %s.uid=%s" % (sql, tablename, jointo)

    def find_tsearch2_schema(self):
        """Looks up for tsearch2.sql in a list of default paths.
        """
        for path in TSEARCH_SCHEMA_PATH:
            for fullpath in glob.glob(path):
                if isfile(fullpath):
                    # tsearch2.sql found !
                    return fullpath
        raise RuntimeError("can't find tsearch2.sql")
    
    def init_extensions(self, cursor, owner=None):
        """If necessary, install extensions at database creation time.
        
        For postgres, install tsearch2 if not installed by the template.
        """
        tstables = []
        for table in self.dbhelper.list_tables(cursor):
            if table.startswith('pg_ts'):
                tstables.append(table)
        if tstables:
            print 'pg_ts_dict already present, do not execute tsearch2.sql'
            if owner:
                print 'reset pg_ts* owners'
                for table in tstables:
                    cursor.execute('ALTER TABLE %s OWNER TO %s' % (table, owner))
        else:
            fullpath = self.find_tsearch2_schema()
            cursor.execute(open(fullpath).read())
            print 'tsearch2.sql installed'

    def sql_init_fti(self):
        """Return the sql definition of table()s used by the full text index.

        Require extensions to be already in.
        """
        return APPEARS_SCHEMA

    def sql_drop_fti(self):
        """Drop tables used by the full text index."""
        return '''DROP INDEX appears_uid;
DROP TABLE appears;'''

    def sql_grant_user(self, user):
        return 'GRANT ALL ON appears TO %s;' % (user)
            
