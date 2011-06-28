# -*- coding: utf-8 -*-
from django import forms
from models import WikiPage

class WikiPageForm(forms.ModelForm):
    class Meta:
        model = WikiPage
        fields = ['text']

