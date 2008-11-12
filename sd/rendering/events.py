# -*- coding: utf-8 -*-

from zope.interface import implements
import interfaces


class ConfigurationSheetEvent(object):
    """A global event that can be trigged for any configuration sheet actions.
    """
    implements(interfaces.IConfigurationSheetEvent)
    
    def __init__(self, object, parent):
        self.object = object
        self.parent = parent


class ConfigurationSheetAdded(ConfigurationSheetEvent):
    """An event that takes place when a configuration sheet is added.
    """
    implements(interfaces.IConfigurationSheetAdded)


class ConfigurationSheetEdited(ConfigurationSheetEvent):
    """An event that takes place when a configuration sheet has been edited.
    """
    implements(interfaces.IConfigurationSheetEdited)
