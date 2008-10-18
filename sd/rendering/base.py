# -*- coding: utf-8 -*-

from Acquisition import Explicit
from zope.interface import implements
from zope.publisher.browser import BrowserPage
from zope.cachedescriptors.property import CachedProperty

from plone.memoize.instance import memoize
from Products.Five.browser import BrowserView

from sd.common.adapters.storage.interfaces import IStorage
from sd.common.adapters.interfaces import IContentQueryHandler
from sd.contents.interfaces import IBatchProvider, IUndirectLayoutProvider
from sd.contents.interfaces import IDynamicStructuredItem
from interfaces import IStructuredRenderer, IBatchedContentProvider


class StructuredRenderer(BrowserView):
    """The base implementation of the structured renderer
    """
    implements(IStructuredRenderer, IUndirectLayoutProvider)

    _filtering = None

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.__parent__ = context

    def __getitem__(self, name):
        return self.index.macros[name]

    @memoize
    def getId(self):
        return self.context.getId()

    @memoize
    def UID(self):
        return self.context.UID()

    @memoize
    def Title(self):
        return self.context.Title()        

    @memoize
    def Description(self):
        return self.context.Description()

    @memoize
    def absolute_url(self):
        return self.context.absolute_url()

    @CachedProperty
    def _edit_url(self):
       return self.absolute_url() + "/@@sd.preferences"
    
    @CachedProperty
    def show_title(self):
        return IDynamicStructuredItem(self.context).show_title

    @CachedProperty
    def show_description(self):
        return IDynamicStructuredItem(self.context).show_description

    @CachedProperty
    def configuration(self):
        return IStorage(self.context).retrieve(self.__name__)

    def javascript(self):
        return NotImplementedError(u"You must implement 'javascript' as a "
                                   u"method or page template file attribute."
                                   u"It must return valid javascript code.")

    def widget(self, *args, **kw):
        return self.context.widget(*args, **kw)

    def __call__(self, *args, **kw):
        return self.index(*args, **kw)
    
    def render(self, *args, **kw):
        if self.__renderer_macro__ is not None:
            return self.index.renderMacro(self.__renderer_macro__, **kw)
        return self.index(*args, **kw)
    

class FolderishRenderer(StructuredRenderer):
    """Extends a StructuredRenderer in order to provide convenient methods
    for both content retrieving and batching.
    """
    implements(IBatchedContentProvider)

    @CachedProperty
    def batch_size(self):
        provider = IBatchProvider(self.context, None)
        if provider is None:
            return 15
        return provider.batch_size

    @CachedProperty
    def batch_name(self):
        return "batch_%s" % self.UID()

    @CachedProperty
    def has_next_page(self):
        if not self.batch_size:
            return False
        current_size = self.batch_size * (self.page + 1)
        return len(self.query_contents()) > current_size

    @memoize
    def contents(self, full_objects=False, **contentFilter):
        brains = self.query_contents(**contentFilter)
        if self.batch_size:
            start = self.batch_size * self.page
            end = start + self.batch_size
            brains = brains[start:end]

        return (full_objects and [brain.getObject() for brain in brains]
                or brains)

    @memoize
    def query_contents(self, **contentFilter):
        iface = getattr(self, '_filtering', None)
        if iface:
            contentFilter['object_provides'] = iface
        handler = IContentQueryHandler(self.context, None)
        return handler and handler.query_contents(**contentFilter) or []

    def get_page(self):
        return (getattr(self, '_page', None) or
                int(self.request.get(self.batch_name, 0)))

    def set_page(self, value):
        self._page = value
            
    page = property(get_page, set_page)
