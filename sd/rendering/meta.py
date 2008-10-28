# -*- coding: utf-8 -*-

import base
import martian
import directives
import grokcore.view
import grokcore.component
import zope.component

from interfaces import IStructuredRenderer, IStructuredDefaultRenderer
from zope.i18nmessageid import MessageFactory
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from grokcore.view.interfaces import ITemplateFileFactory


DEFAULT = u"default"
_ = MessageFactory("sd")


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
        return True


class BaseRendererGrokker(martian.ClassGrokker):
    martian.priority(450)
    martian.component(base.StructuredRenderer)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.view.template, default=None)
    martian.directive(grokcore.component.name, default=DEFAULT)
    martian.directive(directives.target)
    martian.directive(directives.macro)


    def grok(self, name, renderer, module_info=None, **kw):
        renderer.module_info = module_info
        return super(BaseRendererGrokker, self).grok(
            name, renderer, module_info, **kw)

    def execute(self, renderer, config, layer, name,
                macro, target, template, **kw):
        """Register a renderer.
        """        
        provides = (name == DEFAULT and IStructuredDefaultRenderer
                    or IStructuredRenderer)

        renderer.__view_name__ = name
        renderer.__renderer_macro__ = macro
        templates = renderer.module_info.getAnnotation(
            'grok.templates', None
            )
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,               
                args=(templates, renderer.module_info, renderer)
                )
        
        for context in target:
            adapts = (context, layer)
            config.action(
                discriminator=('adapter', adapts, provides, name),
                callable=zope.component.provideAdapter,
                args=(renderer, adapts, provides, name),
                )

        return True

    def checkTemplates(self, templates, module_info, factory):

        def has_render(factory):
            return factory.render != base.GrokAwareRenderer.render

        def has_no_render(factory):
            return (factory.render == base.GrokAwareRenderer.render and
                    getattr(factory, 'template', None) is None)

        templates.checkTemplates(module_info, factory, 'sd.renderer',
                                 has_render, has_no_render)

