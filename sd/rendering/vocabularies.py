# -*- coding: utf-8 -*-

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface.declarations import directlyProvides, implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import ITokenizedTerm, ITitledTokenizedTerm
from zope.component import getAdapters

from sd.contents.interfaces import IUndirectLayoutProvider
from interfaces import IChapterRenderer, IParagraphRenderer
from zope.publisher.browser import TestRequest
from sd import _


class LayoutTerm(object):
    """Simple tokenized keyword used by SimpleVocabulary.
    """
    implements(ITokenizedTerm)
    
    def __init__(self, name, docstring):
        """Create a term from the single value
        This class prevents the use of the silly bugged SimpleTerm.
        """
        self.value = name
        self.token = name
        self.title = _(name, default=docstring)
        directlyProvides(self, ITitledTokenizedTerm)


class ChapterLayoutVocabulary(object):
    """Vocabulary factory.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):

        if IUndirectLayoutProvider.providedBy(context):
            context = getattr(context, 'context', None)
            if not context:
                raise KeyError ("This adapter doesn't provide a suffisant"
                                "context")
        
        renderers = getAdapters((context, TestRequest()), IChapterRenderer)
        terms = [LayoutTerm(name, renderer.__doc__)
                 for name, renderer in renderers]
        return SimpleVocabulary(terms)


class ParagraphLayoutVocabulary(object):
    """Vocabulary factory.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):

        if IUndirectLayoutProvider.providedBy(context):
            context = getattr(context, 'context', None)
            if not context:
                raise KeyError ("This adapter doesn't provide a suffisant"
                                "context")
        
        renderers = getAdapters((context, TestRequest()), IParagraphRenderer)
        terms = [LayoutTerm(name, renderer.__doc__)
                 for name, renderer in renderers]
        return SimpleVocabulary(terms)


ChapterLayoutVocabularyFactory = ChapterLayoutVocabulary()
ParagraphLayoutVocabularyFactory = ParagraphLayoutVocabulary()

__all__ = ("ChapterLayoutVocabularyFactory",
           "ParagraphLayoutVocabularyFactory")
