# -*- coding: utf-8 -*-

import interfaces as rendering
import grokcore.component as grok
from zope.component import queryMultiAdapter, getAdapters
from zope.publisher.interfaces import browser
from zope.cachedescriptors.property import CachedProperty
from sd.contents.interfaces import IStructuredItem, IDynamicStructuredItem

COMPONENT = 1

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

        default = [renderer for renderer in
                   getAdapters((self.context, self.request),
                               rendering.IStructuredDefaultRenderer)]
        return default and default[0][COMPONENT] or None
