"""
Copyright (c) 2000-2003 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr

exceptions for the indexer modules
"""

__revision__ = "$Id: _exceptions.py,v 1.3 2005-02-25 23:24:29 nico Exp $"

class IndexerException(Exception):
    """base class for indexer exception
    """

class UnknownExtension(IndexerException):
    """raised when an unknown extension is encountered
    """
    
class UnknownFileType(IndexerException): 
    """raised when an unknown file type is encountered
    """


class StopWord(Exception):
    """raised to indicate that a stop word has been encountered
    """
