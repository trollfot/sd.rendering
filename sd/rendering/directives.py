# -*- coding: utf-8 -*-

import martian
from martian.error import GrokImportError
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

class traversable(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE
    default = None
    validate = martian.validateText

class configuration(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    default = None

    def factory(self, interface, klass):
        return {'schema': interface,
                'klass': klass}
