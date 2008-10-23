# -*- coding: utf-8 -*-

import base
import martian
import directives
import grokcore.view
import grokcore.component
import zope.component

from interfaces import IStructuredRenderer
from zope.publisher.interfaces.browser import IDefaultBrowserLayer



class FolderishRendererGrokker(martian.ClassGrokker):
    martian.priority(550)
    martian.component(base.FolderishRenderer)
    martian.directive(directives.limit)
    martian.directive(directives.restrict)

    def execute(self, renderer, config, limit, restrict, **kw):
        """Register a renderer.
        """
        renderer.__folder_limit__ = limit
        renderer.__folder_restrict__ = restrict
        print "grokked folderish"
        return True


class BaseRendererGrokker(martian.ClassGrokker):
    martian.priority(450)
    martian.component(base.StructuredRenderer)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, default=u"default")
    martian.directive(directives.macro, name="macro")
    martian.directive(directives.target, name="targets")
    
    def grok(self, name, renderer, module_info=None, **kw):
        renderer.__view_name__ = name
        renderer.module_info = module_info
        return super(BaseRendererGrokker, self).grok(
            name, renderer, module_info, **kw)

    def execute(self, renderer, config, layer, name, macro, targets, **kw):
        """Register a renderer.
        """
        print "grokked other"
        renderer.__renderer_macro__ = macro
        templates = renderer.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, renderer.module_info, renderer)
                )
        
        for context in targets:
            adapts = (context, layer)
            config.action(
                discriminator=('adapter', adapts, IStructuredRenderer, name),
                callable=zope.component.provideAdapter,
                args=(renderer, adapts, IStructuredRenderer, name),
                )

        return True

    def checkTemplates(self, templates, module_info, renderer):
        def has_render(provider):
            return False
        def has_no_render(provider):
            # always has a render method
            return False
        templates.checkTemplates(module_info, renderer,
                                 'structured document renderer',
                                 has_render, has_no_render)
