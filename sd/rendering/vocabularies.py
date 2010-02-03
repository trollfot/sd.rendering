# -*- coding: utf-8 -*-

from five import grok
from sd.contents.interfaces import IUndirectLayoutProvider
from sd.rendering.interfaces import IStructuredRenderer
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.component import getAdapters
from zope.interface.declarations import directlyProvides
from zope.publisher.browser import TestRequest
from zope.schema.interfaces import ITokenizedTerm, ITitledTokenizedTerm
from zope.schema.vocabulary import SimpleVocabulary


class LayoutTerm(object):
    """Simple tokenized keyword used by SimpleVocabulary.
    """
    grok.implements(ITokenizedTerm)

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
