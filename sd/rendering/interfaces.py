# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute


class IStructuredView(Interface):
    """View associated to a structured item.
    """
    def contents(self, full_objects=True):
        """Queries the shown content.
        """

class IStructuredRenderer(Interface):
    """A renderer is an adapter. It has special methods in order to be
    handled by a content provider. It can be used simply as an adapter.
    Named, it can be used in order to provide a dynamic layout.
    """
    def render(self):
        """This has to return a snippet of HTML. Usually, this is
        done by rendering a template.
        """

class IRendererResolver(Interface):
    """An adapter used to fetch the renderers.
    """
    renderer = Attribute("Renderer to use to render the given context.")

class IStructuredDefaultRenderer(IStructuredRenderer):
    """A structured renderer used as default, when no layout is selected.
    """

class IBatchedContentProvider(IStructuredRenderer, IStructuredView):
    """This is an implementation of a batch mixin for a renderer
    """
    batch_size = Attribute("The size of the batch.")
    batch_name = Attribute("The unique name representing the batch in a page.")
    page = Attribute("The number of the page visited.")

    def query_contents(**contentFilter):
        """Queries the shown content. It doesn't limit nor trim the list.
        It returns a list of Brains. If iface is provided, it should
        restrict the returned list to the objects implementing the interface
        or to brains of objects implementing the interface.
        """
        
    def contents(full_objects=False, **contentFilter):
        """Returns the processed batch content.
        It calls the method 'query_contents' and slices it according to
        the current batch position. If 'full_objects' is True, it returns
        a list of objects otherwise brains.
        """
    
