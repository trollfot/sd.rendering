# -*- coding: utf-8 -*-

from five import grok
from Acquisition import aq_parent, aq_inner
from zope.formlib import form
from zope.cachedescriptors.property import CachedProperty
from plone.app.form.validators import null_validator

from directives import configuration
from sd.common.forms.base import base_template
from sd.common.adapters.storage.interfaces import IStorage
from sd.contents.interfaces import IStructuredItem
from sd.rendering.interfaces import IStructuredRenderer, IConfigurationSheet

from zope.i18nmessageid import MessageFactory
from Products.CMFPlone import PloneMessageFactory as __
from Products.statusmessages.interfaces import IStatusMessage

import events
from zope.event import notify
from plone.app.form.events import EditCancelledEvent
from zope.lifecycleevent import ObjectModifiedEvent


_ = MessageFactory("sd")
grok.templatedir("templates")


class EditForm(grok.EditForm):

    grok.name("edit")
    grok.context(IConfigurationSheet)
    grok.require("cmf.ModifyPortalContent")
    grok.template("form")

    form_name = _(u"configuration_form_name",
                  default=u"Rendering customization options")
    label = _(u"configure_display", default=u"Display configuration")

    @CachedProperty
    def renderer(self):
        return aq_parent(aq_inner(self.context))

    @CachedProperty
    def form_fields(self):
        config = configuration.bind().get(self.renderer)
        fields = form.FormFields(config['schema'])
        return fields.omit('name')

    @form.action(__(u"label_save", default="Save"),
                 condition=form.haveInputWidgets, name=u'save')
    def handle_save_action(self, action, data):
        if form.applyChanges(self.context,
                             self.form_fields, data,
                             self.adapters):
            notify(ObjectModifiedEvent(self.context))
            notify(events.ConfigurationSheetEdited(self.context,
                                                   self.__parent__))
            self.status = "Changes saved"
        else:
            notify(EditCancelledEvent(self.context))
            self.status = "No changes"
            
        messager = IStatusMessage(self.request)
        messager.addStatusMessage(self.status, type="configuration")
        self.request.response.redirect(self.context.absolute_url())

    @form.action(__(u"label_cancel", default=u"Cancel"),
                 validator=null_validator, name=u'cancel')
    def handle_cancel_action(self, action, data):
        notify(EditCancelledEvent(self.context))
        self.request.response.redirect(self.context.absolute_url())


class AddForm(grok.AddForm):

    grok.name("configure")
    grok.context(IStructuredRenderer)
    grok.require("cmf.ModifyPortalContent")
    grok.template("form")

    form_name = _(u"configuration_form_name",
                  default=u"Rendering customization options")
    label = _(u"configure_display", default=u"Display configuration")

    @CachedProperty
    def form_fields(self):
        config = configuration.bind().get(self.context)
        fields = form.FormFields(config['schema'])
        return fields.omit('name')
    
    def create(self, data):
        config = configuration.bind().get(self.context)
        factory = config['klass']
        sheet = factory(unicode(self.context.__view_name__))
        form.applyChanges(sheet, self.form_fields, data)
        return sheet

    def createAndAdd(self, data):
        ob = self.create(data)
        return self.add(ob)

    def nextURL(self):
        return self.context.absolute_url()
    
    def add(self, obj):
        storage = IStorage(self.context.context)
        storage.store(obj)
        notify(events.ConfigurationSheetAdded(obj, self.context.context))
        self._finished_add = True
        messager = IStatusMessage(self.request)
        messager.addStatusMessage(u"Configuration done.", type="configuration")
        self.request.response.redirect(self.context.absolute_url())
