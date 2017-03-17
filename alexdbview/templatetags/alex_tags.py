'''
Created on 20.07.2016

@author: michael
'''
import datetime
from django import template
from alexdbview.views import create_rows
from django.template.loader import get_template

register = template.Library()

def referenced_events(referenced_events):
    return {'event_rows': create_rows(referenced_events, 3)}

template = get_template('alex/eventreferences.html')
register.inclusion_tag(template)(referenced_events)