"""Generic Indexer.

:copyright: 2003-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import os
import mimetypes

from indexer.query_objects import tokenize
from indexer._exceptions import UnknownExtension, UnknownFileType

class IIndexableObject:
    """Interface for indexable objects."""
        
    def get_words(self):
        """Return words to be indexed a word should be an unicode string."""
        raise NotImplementedError()


class AttributeIndexableMixIn(IIndexableObject):
    """MixIn which allow to index some predefined attributes of any object.
    """
    
    def __init__(self, indexable_attributes=None):
        if indexable_attributes is not None:
            self.indexable_attributes(indexable_attributes)

    def indexable_attributes(self, indexable_attributes=None):
        """get/set indexable attributes"""
        if indexable_attributes is not None:
            self.__indexable_attributes = indexable_attributes
        else:
            return self.__indexable_attributes
        
    def get_words(self):
        """Return words to be indexed (a word is an unicode string).
        """
        for attr in self.__indexable_attributes:
            value = getattr(self, attr, None)
            if value is None:
                continue
            for word in tokenize(value):
                yield word

class IndexableFile(IIndexableObject):
    """Wrap a file to make it indexable if there is an adapter for it's type.
    """
    
    def __init__(self, url, mime_type=None, encoding='UTF-8'):
        self.url = url
        # get mime_type if necessary
        if mime_type is None:
            mime_type, encoding = mimetypes.guess_type(url)
        if mime_type is None:
            raise UnknownExtension('Unable to get MIME type for %s' % url)
        # get an adapter for this mime type
        try:
            self.adapter = FILE_ADAPTERS[mime_type](encoding)
        except KeyError:
            raise UnknownFileType('Unable to get an adapter for MIME type %s'
                                  % mime_type)
        # XXXFIXME: automaticly guess encoding from file ?
        
    def get_words(self):
        """Return words to be indexed (a word should be an unicode string).
        """
        return self.adapter.get_words(self.url)


# File adapters ###############################################################

class PlainTextAdapter:
    """Adapter for plain text files."""
    
    def __init__(self, encoding='UTF-8'):
        self.encoding = encoding
        
    def get_words(self, url):
        """Return words to be indexed (a word should be an unicode string).
        """
        return self._get_words( open(url) )

    def _get_words(self, buffer):
        """ extract word from a plain text buffer """
        for line in buffer.xreadlines():
            for word in tokenize(unicode(line, self.encoding)):
                yield word

class ConverterAdapter(PlainTextAdapter):
    """
    Abstract class for file adapter using an external command to convert the
    input file to plain text.
    """
    
    def __init__(self, command, encoding='UTF-8'):
        PlainTextAdapter.__init__(self, encoding)
        self.command = command
        
    def get_words(self, url):
        """Return words to be indexed (a word should be an unicode string).
        """
        return self._get_words( os.popen(self.command % url) )

class HTMLAdapter(ConverterAdapter):
    """HTML -> text adapter"""
    def __init__(self, encoding='UTF-8'):
        ConverterAdapter.__init__(self, 'html2text %s', encoding)
        
class PSAdapter(ConverterAdapter):
    """Postscript -> text adapter"""
    def __init__(self, encoding='UTF-8'):
        ConverterAdapter.__init__(self, 'ps2text %s', encoding)
        
class PDFAdapter(ConverterAdapter):
    """PDF -> text adapter"""
    def __init__(self, encoding='UTF-8'):
        ConverterAdapter.__init__(self, 'pdftotext %s', encoding)


FILE_ADAPTERS = {
    'text/plain'    : PlainTextAdapter,
    'text/x-python' : PlainTextAdapter,
    
    'text/html' : HTMLAdapter,
    
    'application/postscript': PSAdapter,
    
    'application/pdf': PDFAdapter,
    }

                
