"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import WikiPage
from django.contrib.auth.models import User

import factory
from model_mommy import mommy

class UserNya(object):
    nya_attr = None

class UserFactory(factory.Factory):
    FACTORY_FOR = UserNya

class WikiPageFactory(factory.Factory):
    FACTORY_FOR = WikiPage
    author = factory.LazyAttribute(lambda a: UserFactory())

class SimpleTest(TestCase):
    def test_basic_addition(self):
        wp = mommy.make_one(WikiPage)
        assert wp.id == 1
        assert wp.author.id == 1

    def test_factory(self):
        u = UserFactory()
        assert u.nya_attr == 10


