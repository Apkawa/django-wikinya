# -*- coding: utf-8 -*-
from django.db import models
from mptt.models import MPTTModel
import reversion

from creole import creole2html


class BaseModel(models.Model):
    datetime_create = models.DateTimeField(auto_now_add=True)
    datetime_update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class WikiPage(MPTTModel, BaseModel):
    author = models.ForeignKey('auth.User')

    title = models.CharField(max_length=512, db_index=True)
    text = models.TextField()

    parent_page = models.ForeignKey('self', null=True, blank=True, related_name='children_pages')

    class Meta:
        get_latest_by = 'datetime_create'
        unique_together = [('title', 'parent_page')]

    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by = []
        parent_attr = 'parent_page'

    @property
    def html_text(self):
        return creole2html(self.text)



class WikiPageMeta(models.Model):
    TYPE_VERSION_CHOICES = (
            ('t', 'edit text'),
            ('m', 'change more attrs')
            )
    revision = models.ForeignKey("reversion.Revision")  # This is required
    type_version = models.CharField(max_length=2, choices=TYPE_VERSION_CHOICES, default='t')


reversion.register(WikiPage)


