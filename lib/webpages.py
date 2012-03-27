#!/usr/bin/python
""" Generic webpages """

__docformat__ = 'epytext en'

######################################################################
## Imports
######################################################################
from django.shortcuts import render_to_response, redirect
from bodhi.models import Device, History
from django.db.models import Count, Max
from datetime import datetime, timedelta

######################################################################
## Views
######################################################################

def homepage(request):
    '''
    Homepage
    '''
    nb = Device.objects.all().aggregate(Count('id'))["id__count"]
    today = datetime.today()
    dev = Device.objects.annotate(time_max=Max('history__timestamp'))
    his = History.objects.filter(action=0, timestamp__in=[d.time_max for d in dev], date=today)
    nb_ON = len(his.filter(result=0))
    nb_OFF = len(his.filter(result=1))
    return render_to_response('index.html', {'nb': nb,
                                             'nb_ON' : nb_ON,
                                             'nb_OFF' : nb_OFF
                                            })

def help(request):
    '''
    Help page
    '''
    return render_to_response('main.html', {'text' : 'To Do'})
