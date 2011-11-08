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
from django.db.models import Sum, Count

from lib.device import wake_on_lan, shutdown_win, shutdown_nix, ping
from lib.karma import Karma
from lib.graphs import history_img

from datetime import datetime, timedelta

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
        record = History.objects.filter(device=device).latest()
        history.append(record)
    return render_to_response('bodhi/list.html', {'history': history})

def device(request, device_id):
    '''
    Display a device
    '''
    dev = get_object_or_404(Device, pk=device_id)
    last = History.objects.filter(device=device_id).latest()
    his = History.objects.filter(device=device_id).exclude(action=0)[0:10]
    power = Device.objects.get(pk=device_id).watt
    today = datetime.today()
    kwh_today = History.objects.filter(device=device_id, action=0, user="cron", result=0, date=today).aggregate(Count('result'))["result__count"] * power / 1000.0
    yesterday = today - timedelta(days=1)
    kwh_day = History.objects.filter(device=device_id, action=0, user="cron", result=0, date=yesterday).aggregate(Count('result'))["result__count"] * power / 1000.0
    week = datetime.today() - timedelta(days=7)
    kwh_week = History.objects.filter(device=device_id, action=0, user="cron", result=0, date__gt=week).aggregate(Count('result'))["result__count"] * power / 1000.0
    img = history_img(device_id, 10)
    return render_to_response('bodhi/device.html',
                                {'device': dev,
                                'kwh_today' : kwh_today,
                                'kwh_day' : kwh_day,
                                'kwh_week': kwh_week,
                                'history' : his,
                                'img' : img,
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
        hf.save(dev, 0, 1)
    else:
        hf.save(dev, 0, not isUp)
    last = History.objects.filter(device=device_id).latest()
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
        error_message = "This device don't allow wakeups."
    else:
        hf = Karma()
        try:
            wake_on_lan(dev.MAC)
        except Exception as e:
            error_message = e.__unicode__()
            hf.save(dev, 1, 1)
        finally:
            hf.save(dev, 1, 0)
    last = History.objects.filter(device=device_id).latest()
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
        last = History.objects.filter(device=device_id).latest()
        his = History.objects.filter(device=device_id)
        return render_to_response('bodhi/device.html',
                                {'device': dev,
                                'history' : his,
                                'latest' : last,
                                'error_message' : error_message})
    else:
        last = History.objects.filter(device=device_id).latest()
        power = Device.objects.get(pk=device_id).watt
        today = datetime.today()
        kwh_today = History.objects.filter(device=device_id, action=0, user="cron", result=0, date=today).aggregate(Count('result'))["result__count"] * power / 1000.0
        yesterday = today - timedelta(days=1)
        kwh_day = History.objects.filter(device=device_id, action=0, user="cron", result=0, date=yesterday).aggregate(Count('result'))["result__count"] * power / 1000.0
        week = datetime.today() - timedelta(days=7)
        kwh_week = History.objects.filter(device=device_id, action=0, user="cron", result=0, date=week).aggregate(Count('result'))["result__count"] * power / 1000.0
        kwh_gain = kwh_week - kwh_today

        if 'reboot' in request.GET and  request.GET["reboot"] == '1' :
            reboot = True
        else:
            reboot = False
        return render_to_response('bodhi/shutdown.html', {'latest': last,
                                                          'kwh_today' : kwh_today,
                                                          'kwh_day' : kwh_day,
                                                          'kwh_week': kwh_week,
                                                          'kwh_gain': kwh_gain,
                                                          'reboot': reboot})

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
        if 'reboot' in request.POST and request.POST['reboot'] == 'on'  :
            action = 3
            reboot = True
        else:
            action = 2
            reboot = False
        try:
            if request.POST['timeout'] :
                timeout = int(request.POST['timeout'])
            else :
                timeout = 5
            if request.POST['password'] :
                password = request.POST['password']
            else :
                password = ''

            if dev.platform == "linux" :
                shutdown_nix(dev.name, request.POST['user'], password,
                             msg=request.POST['message'], reboot=reboot, timeout=timeout)
            else:
                shutdown_win(dev.name, request.POST['user'], password,
                             msg=request.POST['message'], reboot=reboot, timeout=timeout*60)
        except Exception as e:
            error_message = e.__unicode__()
            hf.save(dev, action, 1)
        finally:
            hf.save(dev, action, 0, request.POST['message'])
    last = History.objects.filter(device=device_id).latest()
    his = History.objects.filter(device=device_id)
    return render_to_response('bodhi/device.html',
                                {'device': dev,
                                'history' : his,
                                'latest' : last,
                                'error_message' : error_message})

def history_image(request, device_id, days):

  return HttpResponse(history_img(device_id, days), mimetype='image/svg+xml')
