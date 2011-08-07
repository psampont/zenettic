#!/usr/bin/python
""" Remotely manage network devices via webpages """

__docformat__ = 'epytext en'

######################################################################
## Imports
######################################################################
from bodhi.models import Device, History
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from bodhi.choices import *

from lib.device import wake_on_lan, shutdown, ping
from lib.karma import Karma

######################################################################
## Views
######################################################################

def index(request):
    '''
    Homepage
    '''
    devices = Device.objects.all().order_by('name')
    history = []
    for device in devices :
        record = History.objects.filter(device=device).latest('timestamp')
        history.append(record)
    return render_to_response('bodhi/list.html', {'history': history})

def device(request, device_id):
    '''
    Display a device
    '''
    dev = get_object_or_404(Device, pk=device_id)
    last = History.objects.filter(device=device_id).latest('timestamp')
    his = History.objects.filter(device=device_id)
    return render_to_response('bodhi/device.html',
                                {'device': dev,
                                'history' : his,
                                'latest' : last})

def device_ping(request, device_id):
    '''
    Ping and display a device
    '''

    error_message = None
    dev = get_object_or_404(Device, pk=device_id)
    hf = Karma()
    try:
      isUp=ping(dev.name)
    except Exception as e :
        error_message = e.__unicode__()
        hf.save(dev, 0, -1)
    else:
        hf.save(dev, 0, not isUp)
    last = History.objects.filter(device=device_id).latest('timestamp')
    his = History.objects.filter(device=device_id)
    return render_to_response('bodhi/device.html',
                                {'device': dev,
                                 'history' : his,
                                'latest' : last,
                                'error_message' : error_message})

def device_wol(request, device_id):
    '''
    Wake up a device
    '''
    error_message = None
    dev = get_object_or_404(Device, pk=device_id)
    if dev.wakeup == False :
        error_message = "This device don't allow the shutdown."
    else:
        hf = Karma()
        try:
            wake_on_lan(dev.MAC)
        except Exception as e:
            error_message = e.__unicode__()
            hf.save(dev, 1, -1)
        finally:
            hf.save(dev, 1, 0)
    last = History.objects.filter(device=device_id).latest('timestamp')
    his = History.objects.filter(device=device_id)
    return render_to_response('bodhi/device.html',
                                {'device': dev,
                                'history' : his,
                                'latest' : last,
                                'error_message' : error_message})

def device_ask_pass(request, device_id):
    '''
    Ask password for shutting down a device
    '''
    error_message = None
    dev = get_object_or_404(Device, pk=device_id)
    if dev.shutdown == False :
        error_message = "This device don't allow the shutdown."
        last = History.objects.filter(device=device_id).latest('timestamp')
        his = History.objects.filter(device=device_id)
        return render_to_response('bodhi/device.html',
                                {'device': dev,
                                'history' : his,
                                'latest' : last,
                                'error_message' : error_message})
    else:
        last = History.objects.filter(device=device_id).latest('timestamp')
        return render_to_response('bodhi/shutdown.html', {'latest': last})

def device_shutdown(request, device_id):
    '''
    Shutdown a device
    '''
    error_message = None
    dev = get_object_or_404(Device, pk=device_id)
    if dev.shutdown == False :
        error_message = "This device don't allow the shutdown."
    else:
        hf = Karma()
        try:
            shutdown(dev.name, request.POST['user'], request.POST['password'], timeout=60)
        except Exception as e:
            error_message = e.__unicode__()
            hf.save(dev, 2, -1)
        finally:
            hf.save(dev, 2, 0)
    last = History.objects.filter(device=device_id).latest('timestamp')
    his = History.objects.filter(device=device_id)
    return render_to_response('bodhi/device.html',
                                {'device': dev,
                                'history' : his,
                                'latest' : last,
                                'error_message' : error_message})
