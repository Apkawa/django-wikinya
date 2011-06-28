# -*- coding: utf-8 -*-
import os
from django.db import models
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from django.contrib.contenttypes import generic

from mptt.models import MPTTModel
import reversion

from syntax import wiki2html

from utils.fields import PickledObjectField, ThumbsImageField


class BaseModel(models.Model):
    datetime_create = models.DateTimeField(auto_now_add=True)
    datetime_update = models.DateTimeField(auto_now=True)
    #ip = models.I

    class Meta:
        abstract = True


class WikiPage(MPTTModel, BaseModel):
    author = models.ForeignKey('auth.User')

    title = models.CharField(max_length=512, db_index=True)
    text = models.TextField()

    page_meta_info = PickledObjectField(null=True, blank=True)
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
    def get_object_by_path(cls, path):
        page_path = cls.normal_path(path).split('/')
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

    @staticmethod
    def normal_path(path):
        return path.strip().strip('/')

    @staticmethod
    def get_title_from_path(path):
        spl = WikiPage.normal_path(path).split('/')
        if len(spl) > 1:
            return spl[-1]
        return spl[0]

    def get_source_path(self):
        parent_pages = list(self.get_ancestors().values_list('title', flat=True))
        parent_pages.append(self.title)
        return '/'.join(parent_pages)

    def get_url(self):
        return reverse('wiki_page', kwargs={'page_path':self.get_source_path()})

    @classmethod
    def make_path(self, page_path, kwargs={}, commit=True, skip_last=True):
        path_spl = self.normal_path(page_path).split('/')
        if skip_last:
            path_spl.pop()
        path_spl_length = len(path_spl)
        page_cache = {}
        for n, page_title in enumerate(path_spl, start=1):
            if n == path_spl_length:
                p_p = '/'.join(path_spl)
            else:
                p_p = '/'.join(path_spl[:n])
            page = self.get_object_by_path(p_p)
            if not page:
                page = WikiPage(title=page_title, **kwargs)
            page_cache[page_title] = page


        last = None
        for page_title in path_spl:
            page = page_cache[page_title]
            if not page.id:
                page.parent_page = last
                if commit:
                    page.save()
            last = page
        return [page_cache[pt] for pt in path_spl]



#class WikiLink(models.Model):
#    wiki_link = models.CharField(max_length=256)
#    content_type = models.ForeignKey('contenttypes.ContentType')
#    object_id = models.PositiveIntegerField()
#    source = generic.GenericForeignKey('content_type', 'object_id')

#class WikiBackwardLink(models.Model):
#    link = models.ForeignKey('WikiLink')
#    page = models.ForeignKey('WikiPage')


class WikiPageMeta(models.Model):
    TYPE_VERSION_CHOICES = (
            ('t', 'edit text'),
            ('m', 'change more attrs')
            )
    revision = models.ForeignKey("reversion.Revision")  # This is required
    type_version = models.CharField(max_length=2, choices=TYPE_VERSION_CHOICES, default='t')


class WikiImageAttachementMixin(object):
    @classmethod
    def get_object_by_path(cls, path):
        pages_path, filename = os.path.split(path)
        page = WikiPage.get_object_by_path(pages_path)
        try:
            return cls.objects.filter(page=page, title=filename)[0]
        except IndexError:
            return None

    def get_source_path(self):
        page_path = self.page.get_source_path()
        return os.path.join(page_path, self.title)

def wikiimage_upload_to(instance, filename):
    return 'wiki/images/o/%s'%filename

def wikiimage_thumb_upload_to(orig_filename, size):
    return 'wiki/images/t/%s/%s'%(size, orig_filename)

class WikiImage(BaseModel, WikiImageAttachementMixin):
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

    def get_url(self):
        return self.image.url





def attachement_upload_to(instance, filename):
    if instance.page:
        return 'wiki/attachements/%s/%s' % (instance.page.title, filename)
    else:
        return 'wiki/attachements/%s' % (filename)


class WikiAttachement(BaseModel, WikiImageAttachementMixin):
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

    def get_url(self):
        return self.attach.url

reversion.register(WikiPage)
reversion.register(WikiImage)
reversion.register(WikiAttachement)
