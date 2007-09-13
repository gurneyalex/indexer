import unittest

from logilab.common.testlib import MockConnection
from unittest_default_indexer import IndexableObject

from indexer.query_objects import tokenize
from indexer.postgres8_indexer import PGIndexer
    
class PGIndexerTC(unittest.TestCase):

    def setUp(self):
        self.cnx = MockConnection( () )
        self.indexer = PGIndexer('postgres', self.cnx)
        
    def test_index_object(self):
        self.indexer.index_object(1, IndexableObject())
        self.assertEquals(self.cnx.received,
                          [("INSERT INTO appears(uid, words) VALUES (%(uid)s,to_tsvector('default', %(wrds)s));",
                            {'wrds': 'ginco jpl bla blip blop blap', 'uid': 1})])
        
    def test_execute(self):
        self.indexer.execute(u'ginco-jpl')
        self.assertEquals(self.cnx.received,
                          [("SELECT 1, uid FROM appears WHERE words @@ to_tsquery('default', %(words)s)",
                            {'words': 'ginco&jpl'})])
        

if __name__ == '__main__':
    unittest.main()
