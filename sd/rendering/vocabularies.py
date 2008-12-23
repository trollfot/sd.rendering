# -*- coding: utf-8 -*-

import grokcore.component as grok
from zope.component import getAdapters
from zope.publisher.browser import TestRequest
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import ITokenizedTerm, ITitledTokenizedTerm
from sd.contents.interfaces import IUndirectLayoutProvider
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface.declarations import directlyProvides, implements
from interfaces import IStructuredRenderer


class LayoutTerm(object):
    """Simple tokenized keyword used by SimpleVocabulary.
    """
    implements(ITokenizedTerm)
    
    def __init__(self, name, label):
        """Create a term from the single value. This class prevents
        the use of the silly bugged SimpleTerm.
        """
        self.value = name
        self.token = name
        self.title = label
        directlyProvides(self, ITitledTokenizedTerm)


class LayoutVocabulary(grok.GlobalUtility):
    """Vocabulary factory.
    """
    grok.name(u"sd.rendering.layout")
    grok.implements(IVocabularyFactory)

    def __call__(self, context):

        if IUndirectLayoutProvider.providedBy(context):
            context = getattr(context, 'context', None)
            if not context:
                raise KeyError ("This adapter doesn't provide a suffisant"
                                "context")
        
        renderers = getAdapters((context, TestRequest()), IStructuredRenderer)
        terms = [LayoutTerm(name, renderer.label) for
                 name, renderer in renderers]
        return SimpleVocabulary(terms)
