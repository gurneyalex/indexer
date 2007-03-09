"""
yapps input grammar for indexer queries
"""

from yappsrt import *
from string import *
import re
import sys

class IndexerQueryScanner(Scanner):

    patterns = [
        ("'$'", re.compile('$')),
        ('\\s+', re.compile('\\s+')),
        ('WORD', re.compile('\\w+')),
        ('STRING', re.compile('\'([^\\\'\\\\]|\\\\.)*\'|\\"([^\\\\\\"\\\\]|\\\\.)*\\"')),
    ]
    
    def __init__(self, str):
        Scanner.__init__(self, None, ['\\s+'], str)

class IndexerQuery(Parser):
    def goal(self, Q):
        while self._peek() != "'$'":
            all = self.all(Q)
        self._scan("'$'")

    def all(self, Q):
        _token_ = self._peek('WORD', 'STRING')
        if _token_ == 'WORD':
            WORD = self._scan('WORD')
            Q.add_word(WORD)
        else: # == 'STRING'
            STRING = self._scan('STRING')
            Q.add_phrase(STRING)


def parse(rule, text):
    parser = IndexerQuery(IndexerQueryScanner(text))
    return wrap_error_reporter(parser, rule)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        if len(sys.argv) >= 3:
            f = open(sys.argv[2],'r')
        else:
            f = sys.stdin
        print parse(sys.argv[1], f.read())
    else: print 'Args:  <rule> [<filename>]'
