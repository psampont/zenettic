#!/usr/bin/python
""" Generic webpages """

__docformat__ = 'epytext en'

######################################################################
## Imports
######################################################################
from django.shortcuts import render_to_response, redirect
from bodhi.models import Device, History
from django.db.models import Count
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
    nb_ON = len(History.objects.filter(action=0, result=0, date=today).order_by('device').values('device').distinct())
    nb_OFF = len(History.objects.filter(action=0, result=1, date=today).order_by('device').values('device').distinct())
    return render_to_response('index.html', {'nb': nb,
                                             'nb_ON' : nb_ON,
                                             'nb_OFF' : nb_OFF
                                            })

def help(request):
    '''
    Help page
    '''
    return render_to_response('main.html', {'text' : 'To Do'})
