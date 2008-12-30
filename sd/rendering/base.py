# -*- coding: utf-8 -*-

import martian
import Acquisition

from OFS.SimpleItem import SimpleItem
from zope import component
from zope.interface import Interface, implements
from zope.publisher.interfaces import NotFound
from zope.cachedescriptors.property import CachedProperty
from zope.publisher.browser import BrowserPage
from plone.memoize.instance import memoize

from directives import traversable, configuration
from sd.common.adapters.storage.interfaces import IStorage
from sd.common.adapters.interfaces import IContentQueryHandler
import sd.contents.interfaces as contents 
import interfaces.renderers as rendering
import interfaces.configuration as config


class StructuredRenderer(BrowserPage, SimpleItem):
    """The base implementation of the structured renderer
    """
    traversable("index_html")
    traversable("configuration")
    implements(rendering.IStructuredRenderer,
               contents.IUndirectLayoutProvider)
    
    @property
    def response(self):
        return self.request.response

    def __call__(self):
        return self.template.render(self)

    def publishTraverse(self, request, name):
        allowed = traversable.bind().get(self)
        if allowed and name in allowed:
            return getattr(self, name)
        raise NotFound(self, name, request)

    def default_namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['view'] = self
        return namespace

    def namespace(self):
        return {}

    def redirect(self, url):
        return self.request.response.redirect(url)

    def _render_template(self):
        macro = getattr(self, "__renderer_macro__", None)
        if macro is not None:
            return self.template.renderMacro(self, macro)
        return self.template.render(self)
    
    def render(self):
        return self._render_template()

    @property
    def label(self):
        return NotImplementedError(u"You must have a label as a "
                                   u"string or unicode string.")

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
        return contents.IDynamicStructuredItem(self.context).show_title

    @CachedProperty
    def show_description(self):
        return contents.IDynamicStructuredItem(self.context).show_description

    @CachedProperty
    def configurable(self):
        return configuration.bind().get(self)

    @CachedProperty
    def configuration(self):
        return IStorage(self.context).retrieve(self.__view_name__)

    def javascript(self):
        return NotImplementedError(u"You must implement 'javascript' as a "
                                   u"method or page template file attribute."
                                   u"It must return valid javascript code.")

    def widget(self, *args, **kw):
        return self.context.widget(*args, **kw)

    index_html = render


class FolderishRenderer(StructuredRenderer):
    """Extends a StructuredRenderer in order to provide convenient methods
    for both content retrieving and batching.
    """
    implements(rendering.IBatchedContentProvider,
               rendering.IStructuredView)

    __folder_limit__ = None
    __folder_restrict__ = None

    @CachedProperty
    def batch_size(self):
        provider = contents.IBatchProvider(self.context, None)
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
        if self.__folder_restrict__:
            contentFilter['object_provides'] = [
                ".".join((iface.__module__, iface.__name__))
                for iface in self.__folder_restrict__
                ]

        handler = IContentQueryHandler(self.context, None)      
        return handler and handler.query_contents(
            limit = self.__folder_limit__, **contentFilter
            ) or []

    def get_page(self):
        return (getattr(self, '_page', None) or
                int(self.request.get(self.batch_name, 0)))

    def set_page(self, value):
        self._page = value
            
    page = property(get_page, set_page)


class BaseConfigSheet(SimpleItem):
    implements(config.IConfigurationSheet)

    def __init__(self, name):
        self.name = name
        self.__name__ = name

    def __repr__(self):
        return "<ConfigurationSheet %s>" % self.__name__

    def __call__(self):
        return repr(self)
