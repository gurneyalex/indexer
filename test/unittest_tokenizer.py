# -*- coding: utf-8 -*-

import unittest

from indexer.query_objects import tokenize
from indexer.default_indexer import normalize

def _tokenize(string):
    words = []
    for word in tokenize(string):
        try:
            words.append(normalize(word))
        except StopWord:
            continue
    return words

class TokenizeTC(unittest.TestCase):

    def test_utf8(self):
        self.assertEquals(_tokenize(u'n°2'),
                          ['n2'])
        

if __name__ == '__main__':
    unittest.main()
