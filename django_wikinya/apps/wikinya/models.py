# -*- coding: utf-8 -*-
from django.db import models
from django.utils.safestring import mark_safe

from mptt.models import MPTTModel
import reversion

from syntax import wiki2html

from utils.fields import PickledObjectField, ThumbsImageField


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

    def __unicode__(self):
        return self.title

    @property
    def html_text(self):

        return mark_safe(wiki2html(self.text))

    @classmethod
    def get_page_by_path(cls, path):
        page_path = path.split('/')
        kw = {}
        kw['title'] = page_path[-1]
        for n, piece in enumerate(reversed(page_path[:-1]), start=1):
            field = '%s__title'%'__'.join(['parent_page']*n)
            kw[field] = piece
        #query = models.Q()
        #for field, value in kw.iteritems():
        #    query |= models.Q(**{field:value})
        pages = WikiPage.objects.filter(**kw)
        try:
            return pages[0]
        except IndexError:
            return None



class WikiPageMeta(models.Model):
    TYPE_VERSION_CHOICES = (
            ('t', 'edit text'),
            ('m', 'change more attrs')
            )
    revision = models.ForeignKey("reversion.Revision")  # This is required
    type_version = models.CharField(max_length=2, choices=TYPE_VERSION_CHOICES, default='t')



def wikiimage_upload_to(instance, filename):
    return 'wiki/images/o/%s'%filename

def wikiimage_thumb_upload_to(orig_filename, size):
    return 'wiki/images/t/%s/%s'%(size, orig_filename)

class WikiImage(BaseModel):
    title = models.CharField(null=True, blank=True, max_length=256)
    image = ThumbsImageField(upload_to=wikiimage_upload_to, thumb_upload_to=wikiimage_thumb_upload_to,
            thumb_sizes=[128, 256, 512, 1024])
    meta_info = PickledObjectField(blank=True, null=True)
    page = models.ForeignKey('WikiPage', null=True, blank=True, related_name='images')

    author = models.ForeignKey('auth.User')
    class Meta:
        get_latest_by = 'datetime_create'
        unique_together = [('title', 'page')]

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.imagee

        super(WikiImage, self).save(*args, **kwargs)

def attachement_upload_to(instance, filename):
    if instance.page:
        return 'wiki/attachements/%s/%s' % (instance.page.title, filename)
    else:
        return 'wiki/attachements/%s' % (filename)


class WikiAttachement(BaseModel):
    title = models.CharField(null=True, blank=True, max_length=256)
    attach = models.FileField(upload_to=attachement_upload_to)
    meta_info = PickledObjectField(blank=True, null=True)
    page = models.ForeignKey('WikiPage', null=True, blank=True, related_name='attachements')
    author = models.ForeignKey('auth.User')

    class Meta:
        get_latest_by = 'datetime_create'
        unique_together = [('title', 'page')]

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.attach.name

        super(WikiAttachement, self).save(*args, **kwargs)

reversion.register(WikiPage)
reversion.register(WikiImage)
reversion.register(WikiAttachement)
