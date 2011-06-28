# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from functools import wraps

def render_to(template_name, title='Main'):
    """
    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

    - template: template name to use
    http://djangosnippets.org/snippets/821/
    https://gist.github.com/1048579
    """
    def renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple, dict)):
                if isinstance(output, (list, tuple)):
                    template = output[1]
                    context = output[0]
                elif isinstance(output, dict):
                    template = template_name
                    context = output
                if not 'title' in context:
                    context['title'] = title
                return render_to_response(template, context, RequestContext(request))
            return output
        return wrapper
    return renderer
