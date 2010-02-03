# -*- coding: utf-8 -*-

from five import grok
import interfaces as rendering
from zope.component import queryMultiAdapter
from zope.publisher.interfaces import browser
from zope.cachedescriptors.property import CachedProperty
from sd.common.adapters import storage
from sd.common.fields.annotation import AdapterAnnotationProperty
from sd.contents.interfaces import IStructuredItem, IDynamicStructuredItem


class RendererResolver(grok.MultiAdapter):
    grok.adapts(IStructuredItem, browser.IBrowserRequest)
    grok.implements(rendering.IRendererResolver)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = IDynamicStructuredItem(context, None)

    @CachedProperty
    def renderer(self):

        name = self.adapted and self.adapted.sd_layout or None
        if name is None:
            return None

        if name != u"default":
            return queryMultiAdapter((self.context, self.request),
                                     rendering.IStructuredRenderer,
                                     name = name)

        return queryMultiAdapter((self.context, self.request),
                                 rendering.IStructuredDefaultRenderer,
                                 name = name)


class ConfigurationStorage(storage.GenericAnnotationStorage):
    """Stores a configuration sheet onto the object in an annotation.
    """
    grok.context(IStructuredItem)
    grok.provides(storage.IStorage)

    storage = AdapterAnnotationProperty(
        storage.IDictStorage['storage'],
        ns="sd.rendering.configuration"
        )
