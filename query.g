""" yapps input grammar for indexer queries
"""

__revision__ = "$Id: query.g,v 1.2 2006-03-06 12:55:44 syt Exp $"



%%

parser IndexerQuery:

    ignore:         r'\s+'
    token WORD:     r'\w+'
    token STRING:      r"'([^\'\\]|\\.)*'|\"([^\\\"\\]|\\.)*\""

rule goal<<Q>> : all<<Q>> * '$'

rule all<<Q>>  : WORD    {{ Q.add_word(WORD) }}
               | STRING  {{ Q.add_phrase(STRING) }}
