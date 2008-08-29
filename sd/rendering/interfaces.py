# -*- coding: utf-8 -*-
from zope.interface import Interface, Attribute
from zope.contentprovider.interfaces import IContentProvider

# Renderers
class IBaseStructuredRenderer(Interface):
    """A render is an adapter. It has special methods in order to be
    handled by a content provider. It can be used simply as an adapter.
    Named, it can be used in order to provide a dynamic layout.
    """
    def render(self):
        """This has to return a snippet of HTML. Usually, this is
        done by rendering a template.
        """

class IChapterRenderer(IBaseStructuredRenderer):
    """A renderer for a chapter.
    """

class IParagraphRenderer(IBaseStructuredRenderer):
    """A renderer for a paragraph.
    """
    
class IBatchedContentProvider(Interface):
    """This is an implementation of a batch mixin for a renderer
    """
    batch_size = Attribute("The size of the batch.")
    batch_name = Attribute("The unique name representing the batch in a page.")
    page = Attribute("The number of the page visited.")

    def query_contents(full_objects=False):
        """Returns the processed batch content.
        It calls the method 'contents' and slices it according to the current
        batch position.
        """

    def contents(iface=None, full_objects=False):
        """Queries the shown content. It doesn't limit nor trim the list.
        If 'full_objects' is True, it returns a list of objects.
        Else, it returns a list of Brains. If iface is provided, it should
        restrict the returned list to the objects implementing the interface
        or to brains of objects implementing the interface.
        """

# Content providers
class IStructuredContentProvider(IContentProvider):
    """Marker interface for content providers associated with
    structured document's types.
    """
    template = Attribute("The rendered template.")

class IStructuredDocumentChaptering(IStructuredContentProvider):
    """A content provider that is used to render chapters located
    inside a structured document. They can be used only from a specific view.
    Look at sd.rendering.browser.interfaces.IStructuredDocumentView
    """
    chapters = Attribute("A list of chapters")

class IStructuredDocumentParagraphing(IStructuredContentProvider):
    """A content provider that is used to render paragraphs located
    inside a structured chapter. They can be used only from a specific view.
    Look at sd.rendering.browser.interfaces.IStructuredChapterView
    """
    paragraphs = Attribute("A list of paragraphs")


# Specific views
class IStructuredDocumentView(Interface):
    """View associated to a structured document.
    """
    def chapters(self):
        """This method must return a list of IStructuredChapter objects.
        """
        
class IStructuredChapterView(Interface):
    """View associated to a structured chapter.
    """
    context = Attribute("The context being used to render")
    can_modify_content = Attribute("Boolean")
    can_add_content = Attribute("Boolean")

    def render(self):
        """The rendering method
        """

    def paragraphs(self):
        """This method must return a list of IStructuredParagraph objects.
        """
