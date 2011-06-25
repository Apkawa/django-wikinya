# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath('..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
try:
    from apps.django_virtualenv import init_env
    init_env()
except ImportError:
    pass
    print 'error'
