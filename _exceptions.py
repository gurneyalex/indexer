"""Exceptions for the indexer modules.

:copyright: 2003-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

class IndexerException(Exception):
    """Base class for indexer exception."""

class UnknownExtension(IndexerException):
    """Raised when an unknown extension is encountered."""
    
class UnknownFileType(IndexerException): 
    """Raised when an unknown file type is encountered."""

class StopWord(Exception):
    """Raised to indicate that a stop word has been encountered."""
