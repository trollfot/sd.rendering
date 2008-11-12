# -*- coding: utf-8 -*-

from zope.schema import Object
from zope.interface import Interface
from sd.contents.interfaces import IStructuredItem
from sd.common.adapters.storage.interfaces import IStorageItem


class IConfigurableRenderer(Interface):
    """A marker interface that tags the renderers
    with a linked configuration sheet.
    """

class IConfigurationSheet(IStorageItem):
    """A configuration sheet.
    """

class IConfigurationSheetEvent(Interface):
    """Event trigged when a configuration sheet is involved.
    """
    object =  Object(
        title=u"The sheet of configuration.",
        schema=IConfigurationSheet
        )
    
    parent = Object(
        title=u"The object on which the configuration is stored.",
        schema=IStructuredItem
        )

class IConfigurationSheetAdded(IConfigurationSheetEvent):
    """Event marker interface.
    """

class IConfigurationSheetEdited(IConfigurationSheetEvent):
    """Event marker interface.
    """

__all__ = ("IConfigurableRenderer",
           "IConfigurationSheet",
           "IConfigurationSheetEvent",
           "IConfigurationSheetAdded",
           "IConfigurationSheetEdited")
