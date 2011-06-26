# -*- coding: utf-8 -*-
import os
import urlparse

from xml.sax.saxutils import escape

from creole import creole2html
from creole.creole2html.parser import BlockRules, CreoleParser
from creole.creole2html.emitter import HtmlEmitter

from django.core.urlresolvers import reverse

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

class Link(BaseTag):
    tag_name = 'a'

    def validate(self):
        if 'href' not in self.attrs and 'name' not in self.attrs:
            raise TagException('not exists href or name')

    def parse(self):
        href = self.attrs['href']
        parse_href = urlparse.urlparse(href)
        if not parse_href.scheme:
            self.add_attr('class', 'wikilink')
            from models import WikiPage
            page = WikiPage.get_page_by_path(parse_href.path)
            if not page:
                self.add_attr('class', 'no_wiki_page')
            self.set_attr('href', reverse('wiki_page', kwargs={'page_path':href}))


class WikinyaHtmlEmitter(HtmlEmitter):
    def _make_link(self, href, inside):
        parse_href = urlparse.urlparse(href)
        attrs = {}
        if not parse_href.scheme:
            attrs = {'class':['wikilink']}
            from models import WikiPage
            page = WikiPage.get_page_by_path(parse_href.path)
            if not page:
                attrs['class'].append('no_wiki_page')
            href = os.path.join('/wiki', href)
        return href, inside, attrs


    def link_emit(self, node):
        target = node.content
        if node.children:
            inside = self.emit_children(node)
        else:
            inside = self.html_escape(target)

        link = Link(text=inside, attrs={'href':target})
        link.validate()
        link.parse()
        return link.render()

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
