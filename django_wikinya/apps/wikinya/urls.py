# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    # Examples:
    url(r'^(?P<page_path>.*)$', views.wiki_page , name='home'),
)
