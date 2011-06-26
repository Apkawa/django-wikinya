# -*- coding: utf-8 -*-
from reversion.admin import VersionAdmin
from models import WikiPage, WikiImage, WikiAttachement

from django.contrib import admin

class WikiPageAdmin(VersionAdmin):
    model = WikiPage

admin.site.register(WikiPage, WikiPageAdmin)
admin.site.register(WikiImage)
admin.site.register(WikiAttachement)
