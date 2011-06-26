# -*- coding: utf-8 -*-
import os
import re
import urlparse

from xml.sax.saxutils import escape


from creole import creole2html
from creole.creole2html.parser import BlockRules, CreoleParser
from creole.creole2html.emitter import HtmlEmitter

from django.core.urlresolvers import reverse
from django.http import QueryDict


class TagException(Exception):
    pass

class BaseTag(object):
    tag_name = ''
    def __init__(self, text=None, attrs=None):
        self.text = text
        self.attrs = attrs or {}

    def html_escape(self, text):
        return escape(text)

    def attr_escape(self, text):
        return self.html_escape(text).replace('"', '&quot')

    def set_attr(self, name, value):
        self.attrs[name] = value

    def add_attr(self, name, value):
        if name not in self.attrs:
            self.set_attr(name, [])
        elif not isinstance(self.attrs[name], (list, tuple)):
            self.set_attr(name, [self.attrs[name]])
        self.attrs[name].append(value)

    def validate(self):
        pass

    def parse(self):
        pass

    def _make_attrs(self, attrs=None):
        str_attrs = []
        attrs = attrs or self.attrs
        for a, val in attrs.iteritems():
            if isinstance(val, (list, tuple)):
                val = ' '.join(map(self.attr_escape,val))
            str_attrs.append('%s="%s"'%(a, self.attr_escape(val)))
        return ' '.join(str_attrs)

    def render(self):
        if self.text is None:#self closed tag
            return u"<%(tag_name)s %(attrs)s/>"%{
                    'tag_name':self.tag_name,
                    'attrs': self._make_attrs() }
        else:
            return u"<%(tag_name)s %(attrs)s>%(text)s</%(tag_name)s>"%{
                    'tag_name':self.tag_name,
                    'attrs': self._make_attrs(),
                    'text': self.text,
                    }

class SourceLinkMixin(object):
    '''
    image:namespace/img.jpg
    attach:namespace/attach.zip
    '''
    source_re = re.compile(r'^(?P<type>image|attach|page):(?P<path>.*?)(?:\?(?P<args>.*)|)$')

    def parse_source(self, path):
        match = self.source_re.match(path)
        if match:
            groups = match.groupdict()
            #parse_path = urlparse.urlparse(groups['path'])
            #groups['path'] = parse_path.path
            groups['args'] = QueryDict(groups['args'])
            return groups



    def get_source_model(self, source_type):
        from models import WikiImage, WikiAttachement, WikiPage
        if source_type == 'image':
            return WikiImage
        elif source_type == 'attach':
            return WikiAttachement
        elif source_type == 'page':
            return WikiPage

    def get_source_object(self, path):
        parsed_source = self.parse_source(path)
        if parsed_source:
            source_model = self.get_source_model(parsed_source['type'])
            return source_model.get_object_by_path(parsed_source['path'])




class LinkTag(BaseTag, SourceLinkMixin):
    tag_name = 'a'

    def validate(self):
        if 'href' not in self.attrs and 'name' not in self.attrs:
            raise TagException('not exists href or name')

    def parse(self):
        href = self.attrs['href']
        parse_source = self.parse_source(href)
        if parse_source:
            self.add_attr('class', 'wiki_link')
            source_model = self.get_source_model(parse_source['type'])
            source = source_model.get_object_by_path(parse_source['path'])
            if not source:
                self.add_attr('class', 'no_wiki_page')
                self.set_attr('href', reverse('wiki_page',
                                kwargs={'page_path':parse_source['path']}))
            else:
                self.set_attr('href', source.get_url() )

class ImgTag(BaseTag, SourceLinkMixin):
    tag_name = 'img'
    sizes_map = {
            'small': 256,
            'medium': 512,
            'large': 1024,

            }
    def validate(self):
        if 'src' not in self.attrs:
            raise TagException('not exists href or name')

    def parse(self):
        href = self.attrs['src']
        parse_source = self.parse_source(href)
        if parse_source:
            self.add_attr('class', 'wiki_image')
            source_model = self.get_source_model(parse_source['type'])
            source = source_model.get_object_by_path(parse_source['path'])
            if not source:
                self.add_attr('class', 'wiki_broken_img')
                self.set_attr('src', 'default.img')
            else:
                args = parse_source['args']
                for a in ['title', 'alt']:
                    self.set_attr(a, source.title)
                if 'h' in args:
                    self.set_attr('height',args['h'])
                if 'w' in args:
                    self.set_attr('width',args['w'])

                if parse_source['type'] == 'image':
                    img_url = source.get_url()
                    for key, size in self.sizes_map.iteritems():
                        if key in args:
                            img_url = getattr(source.image, 'url_%s'%size)
                            break

                    self.set_attr('src', img_url)
                else:
                    self.set_attr('src', source.get_url() )


class WikinyaHtmlEmitter(HtmlEmitter):
    def link_emit(self, node):
        target = node.content
        if node.children:
            inside = self.emit_children(node)
        else:
            inside = self.html_escape(target)

        link = LinkTag(text=inside, attrs={'href':target})
        link.validate()
        link.parse()
        return link.render()

    def image_emit(self, node):
        target = node.content
        text = self.attr_escape(self.get_text(node))

        img = ImgTag(attrs={'src':target, 'title':text, 'alt':text})
        img.validate()
        img.parse()
        return img.render()

def wiki2html(text):
    return creole2html(text, debug=True)

def creole2html(markup_string, debug=False, parser_kwargs={}, emitter_kwargs={}):
    """
convert creole markup into html code

>>> creole2html(u'This is **creole //markup//**!')
u'<p>This is <strong>creole <i>markup</i></strong>!</p>\\n'
"""
    assert isinstance(markup_string, unicode)

    # Create document tree from creole markup
    document = CreoleParser(markup_string, **parser_kwargs).parse()
    if debug:
        document.debug()

    # Build html code from document tree
    #print "creole2html HtmlEmitter kwargs:", emitter_kwargs
    return WikinyaHtmlEmitter(document, **emitter_kwargs).emit()
