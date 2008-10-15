# -*- coding: utf-8 -*-

from Acquisition import Explicit
from zope.interface import implements
from zope.publisher.browser import BrowserPage
from zope.cachedescriptors.property import Lazy, CachedProperty

from plone.memoize.instance import memoize
from Products.Five.browser import BrowserView
from Products.ATContentTypes.interface.topic import IATTopic

from sd.common.adapters.storage.interfaces import IStorage
from sd.common.adapters.interfaces import IContentQueryHandler
from sd.contents.interfaces import IBatchProvider
from sd.contents.interfaces import IUndirectLayoutProvider
from sd.contents.interfaces import IDynamicStructuredChapter
from sd.contents.interfaces import IDynamicStructuredParagraph
from interfaces import *


class BaseStructuredContentProvider(Explicit):
    """The base implementation of the structured content provider.
    """
    implements(IStructuredContentProvider)
    
    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = view

    def update(self):
        pass

    def render(self):
        raise NotImplementedError(u"You must implement 'render' as a method "
                                  u"or page template file attribute")


class BaseStructuredRenderer(Explicit, BrowserPage):
    """The base implementation of the structured renderer
    """
    implements(IBaseStructuredRenderer, IUndirectLayoutProvider)

    _filtering = None
    _namespace = u""
    _edit_url = u""

    def __init__(self, context, request):
        BrowserPage.__init__(self, context, request)
        self.__parent__ = context

    def __getitem__(self, name):
        return self.index.macros[name]

    def getId(self):
        return self.context.getId()

    def UID(self):
        return self.context.UID()

    def Title(self):
        return self.context.Title()        
    
    def Description(self):
        return self.context.Description()

    def absolute_url(self):
        return self.context.absolute_url()

    @Lazy
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


class ChapterStructuredRenderer(BaseStructuredRenderer):
    """Extends a BaseStructuredRenderer in order to render specifically a
    chapter.
    """
    implements(IStructuredChapterView, IChapterRenderer)
    _namespace = "sd.rendering.chapter_layout"

    @property
    def _edit_url(self):
       return self.absolute_url() + "/dynamic_chapter"

    @Lazy
    def show_title(self):
        return IDynamicStructuredChapter(self.context).show_title

    @Lazy
    def show_description(self):
        return IDynamicStructuredChapter(self.context).show_description


class ParagraphStructuredRenderer(BaseStructuredRenderer):
    """Extends a BaseStructuredRenderer in order to render specifically a
    paragraph.
    """
    implements(IParagraphRenderer)
    _namespace = "sd.rendering.paragraph_layout"
    
    @property
    def _edit_url(self):
       return self.absolute_url() + "/dynamic_paragraph"
    
    @Lazy
    def show_title(self):
        return IDynamicStructuredParagraph(self.context).show_title

    @Lazy
    def show_description(self):
        return IDynamicStructuredParagraph(self.context).show_description


class FolderishRenderer(BaseStructuredRenderer):
    """Extends a BaseStructuredRenderer in order to provide convenient methods
    for both content retrieving and batching.
    """
    implements(IBatchedContentProvider)

    @Lazy
    def batch_size(self):
        provider = IBatchProvider(self.context, None)
        if provider is None:
            return 15
        return provider.batch_size

    @property
    def batch_name(self):
        return "batch_%s" % self.UID()

    @Lazy
    def has_next_page(self):
        if not self.batch_size:
            return False
        current_size = self.batch_size * (self.page + 1)
        return len(self.query_contents()) > current_size

    @memoize
    def contents(self, contentFilter={}, full_objects=False):
        brains = self.query_contents(contentFilter)
        if self.batch_size:
            start = self.batch_size * self.page
            end = start + self.batch_size
            brains = brains[start:end]

        return (full_objects and [brain.getObject() for brain in brains]
                or brains)

    def query_contents(self, contentFilter={}):
        iface = getattr(self, '_filtering', None)
        if iface:
            contentFilter['object_provides'] = iface
        handler = IContentQueryHandler(self.context, None)
        return handler and handler.query_contents(contentFilter) or []

    def get_page(self):
        return (getattr(self, '_page', None) or
                int(self.request.get(self.batch_name, 0)))

    def set_page(self, value):
        self._page = value
            
    page = property(get_page, set_page)
