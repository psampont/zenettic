#!/usr/bin/python
""" Generic webpages """

__docformat__ = 'epytext en'

######################################################################
## Imports
######################################################################

from django.shortcuts import render_to_response, redirect

######################################################################
## Views
######################################################################

def homepage(request):
    '''
    Homepage
    '''
    return redirect('/bodhi/')

def help(request):
    '''
    Help page
    '''
    return render_to_response('main.html', {'text' : 'To Do'})
