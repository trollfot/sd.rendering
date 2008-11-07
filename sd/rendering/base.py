# -*- coding: utf-8 -*-

import martian
import Acquisition
from directives import traversable
from zope import component
from zope.interface import Interface, implements
from zope.publisher.interfaces import NotFound
from zope.cachedescriptors.property import CachedProperty
from zope.publisher.browser import BrowserPage
from plone.memoize.instance import memoize
from sd.common.adapters.storage.interfaces import IStorage
from sd.common.adapters.interfaces import IContentQueryHandler
from sd.contents.interfaces import IBatchProvider, IUndirectLayoutProvider
from sd.contents.interfaces import IDynamicStructuredItem
from interfaces import IStructuredRenderer, IBatchedContentProvider, IStructuredView


class GrokAwareRenderer(BrowserPage, Acquisition.Explicit):

    getPhysicalPath = Acquisition.Acquired

    def __init__(self, context, request):
        super(GrokAwareRenderer, self).__init__(context, request)
        self.static = component.queryAdapter(
            self.request,
            Interface,
            name=self.module_info.package_dotted_name
            )

        if not (self.static is None):
            self.static = self.static.__of__(self)
    
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
        namespace['static'] = self.static
        namespace['view'] = self
        return namespace

    def namespace(self):
        return {}

    def redirect(self, url):
        return self.request.response.redirect(url)

    def update(self):
        pass

    def _render_template(self):
        macro = getattr(self, "__renderer_macro__", None)
        if macro is not None:
            return self.template.renderMacro(self, macro)
        return self.template.render(self)
    
    def render(self):
        return self._render_template()


class StructuredRenderer(GrokAwareRenderer):
    """The base implementation of the structured renderer
    """
    implements(IStructuredRenderer, IUndirectLayoutProvider)
    traversable("configuration")

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
        return IDynamicStructuredItem(self.context).show_title

    @CachedProperty
    def show_description(self):
        return IDynamicStructuredItem(self.context).show_description

    @CachedProperty
    def configuration(self):
        return IStorage(self.context).retrieve(self.__view_name__)

    def javascript(self):
        return NotImplementedError(u"You must implement 'javascript' as a "
                                   u"method or page template file attribute."
                                   u"It must return valid javascript code.")

    def widget(self, *args, **kw):
        return self.context.widget(*args, **kw)


class FolderishRenderer(StructuredRenderer):
    """Extends a StructuredRenderer in order to provide convenient methods
    for both content retrieving and batching.
    """
    implements(IBatchedContentProvider, IStructuredView)

    __folder_limit__ = None
    __folder_restrict__ = None

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
