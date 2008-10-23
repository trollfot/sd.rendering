# -*- coding: utf-8 -*-

import martian
from zope.interface.interfaces import IInterface
from martian.error import GrokError, GrokImportError
from Products.ATContentTypes.interface import IATContentType

def validateInteger(directive, value):
    if not isinstance(value, int):
        raise GrokImportError("The '%s' directive can only be called with "
                              "integer." % directive.name)


class target(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.MULTIPLE
    default = [IATContentType]
    validate = martian.validateInterface

class macro(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    validate = martian.validateText

class limit(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    validate = validateInteger

class restrict(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE
    default = None
    validate = martian.validateInterface
