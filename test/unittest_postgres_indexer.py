import unittest

from logilab.common.testlib import MockConnection
    
from indexer.query_objects import tokenize
from indexer.postgres_indexer import PGIndexer

class IndexableObject:
    def get_words(self):
        return tokenize('ginco-jpl bla blip blop blop')
    
class PGIndexerTC(unittest.TestCase):

    def setUp(self):
        self.cnx = MockConnection( () )
        self.indexer = PGIndexer('postgres', self.cnx)
        
    def test_index_object(self):
        self.indexer.index_object(1, IndexableObject())
        self.assertEquals(self.cnx.received,
                          [('INSERT INTO appears(uid, words) VALUES (%(uid)s,%(wrds)s);',
                            {'wrds': 'ginco jpl bla blip blop blop', 'uid': 1})
                           ])
        
    def test_execute(self):
        self.indexer.execute('ginco-jpl')
        self.assertEquals(self.cnx.received,
                          [("SELECT 1, uid FROM appears WHERE words @@ 'ginco&jpl'",
                            None)
                           ])
        

if __name__ == '__main__':
    unittest.main()
