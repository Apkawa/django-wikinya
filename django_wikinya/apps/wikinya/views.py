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
from utils.decorators import render_to

from models import WikiPage
from forms import WikiPageForm


@render_to('wikinya.page')
def wiki_page(request, page_path):
    page = WikiPage.get_object_by_path(page_path)
    edit_action = 'edit' in request.GET
    if edit_action:
        return wiki_page_edit(request, page_path, page)

    context = {}
    context['page'] = page
    return context

@render_to('wikinya.page_edit')
@revision.create_on_success
def wiki_page_edit(request, page_path, _page_obj=None):
    page = _page_obj or WikiPage.get_object_by_path(page_path)

    preview_action = request.POST and 'preview' in request.POST

    if request.POST:
        form = WikiPageForm(data=request.POST, initial={'author':request.user}, instance=page)
        if form.is_valid():
            page = form.save(commit=False)
            if not preview_action:
                pages = WikiPage.make_path(page_path, kwargs={'author':request.user})
                if pages:
                    page.parent_page = pages[-1]
                page.title = WikiPage.get_title_from_path(page_path)
                print page_path
                print page.title
                page.author = request.user
                page.save()
                return redirect('wiki_page', page_path=page_path)
    else:
        form = WikiPageForm(initial={'author':request.user}, instance=page)
    context = {}
    context['page'] = page
    context['page_path'] = page_path
    context['form'] = form
    context['preview_action'] = preview_action
    return context

