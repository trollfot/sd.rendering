# -*- coding: utf-8 -*-

from zope.component import getAdapters
from zope.i18nmessageid import MessageFactory
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface.declarations import directlyProvides, implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import ITokenizedTerm, ITitledTokenizedTerm
from zope.publisher.browser import TestRequest

from sd.contents.interfaces import IUndirectLayoutProvider
from interfaces import IStructuredRenderer

_ = MessageFactory("sd")


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


class LayoutVocabulary(object):
    """Vocabulary factory.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):

        if IUndirectLayoutProvider.providedBy(context):
            context = getattr(context, 'context', None)
            if not context:
                raise KeyError ("This adapter doesn't provide a suffisant"
                                "context")
        
        renderers = getAdapters((context, TestRequest()), IStructuredRenderer)
        terms = [LayoutTerm(name, renderer.__doc__)
                 for name, renderer in renderers]
        return SimpleVocabulary(terms)


LayoutVocabularyFactory = LayoutVocabulary()

__all__ = ("LayoutVocabularyFactory",)
