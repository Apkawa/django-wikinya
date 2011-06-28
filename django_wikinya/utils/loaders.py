# -*- coding: utf-8 -*-
import os

from django.template.loaders.filesystem import Loader as FileSystemLoader
from django.template.base import TemplateDoesNotExist

from django.conf import settings
from django.db.models.loading import get_app

class DotLoader(FileSystemLoader):
    '''
    Loading templates by path

    app.template_name -> app/templates/template_name.html
    app.subdir.template_name -> app/templates/subdir/template_name.html

    '''
    def get_template_sources(self, template_name, template_dirs=None):
        app_name, template_name = template_name.split('.',1)

        if not template_dirs:
            template_dirs = []
        try:
            template_dir = os.path.join(os.path.dirname(get_app(app_name).__file__), 'templates')
        except Exception:
            raise TemplateDoesNotExist
        template_dirs.append(template_dir)
        template_name = '%s.html'%template_name.replace('.','/')
        return super(DotLoader, self).get_template_sources(template_name, template_dirs)


