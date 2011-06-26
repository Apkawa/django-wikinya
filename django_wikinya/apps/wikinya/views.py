# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.core.urlresolvers import reverse

from django.http import Http404

from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import get_list_or_404, redirect, get_object_or_404

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from reversion import revision


from utils.shortcuts import render_template
from models import WikiPage

@revision.create_on_success
def wiki_page(request, page_path):
    page = WikiPage.get_object_by_path(page_path)
    if not page:
        raise Http404("not page")
    context = {}
    context['page'] = page
    return render_template(request, 'page.html', context)

