# -*- coding: utf-8 -*-

from StringIO import StringIO
from five import grok
from zope.tal.talinterpreter import TALInterpreter
from five.grok.components import ZopeTwoPageTemplate
from grokcore.view.interfaces import ITemplateFileFactory
from Products.PageTemplates.Expressions import getEngine


class ViewPageTemplateAndMacroFile(ZopeTwoPageTemplate):
    """This page template class handle to render only a macro in it.
    """    
    def renderMacro(self, view, name, **kwargs):
        """Render the given macro in Python code.
        """
        self._template._cook_check()
            
        if self._template._v_errors:
            e = str(self._template._v_errors)
            return 'Page Template %s has errors: %s' % (self._template.id, e)
        
        output = StringIO()
        context = view.default_namespace()
        context.update(kwargs)

        engine = TALInterpreter(self._template._v_program,
                                self._template._v_macros,
                                getEngine().getContext(context),
                                output, strictinsert=0)
        engine.interpret(self._template._v_macros[name])
        return output.getvalue()


class ViewPageTemplateAndMacroFileFactory(grok.GlobalUtility):
    grok.implements(ITemplateFileFactory)
    grok.name('mpt')

    def __call__(self, filename, _prefix=None):
        return ViewPageTemplateAndMacroFile(filename=filename, _prefix=_prefix)
