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

from lib.device import wake_on_lan, shutdown_win, shutdown_nix, ping
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
        record = History.objects.filter(device=device).latest()
        history.append(record)
    return render_to_response('bodhi/list.html', {'history': history})

def device(request, device_id):
    '''
    Display a device
    '''
    dev = get_object_or_404(Device, pk=device_id)
    last = History.objects.filter(device=device_id).latest()
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
            hf.save(dev, 1, -1)
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

        if 'reboot' in request.GET and  request.GET["reboot"] == '1' :
            reboot = True
        else:
            reboot = False
        return render_to_response('bodhi/shutdown.html', {'latest': last,
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
                timeout = request.POST['timeout']
            else :
                timeout = 5
            if dev.platform == "linux" :
                shutdown_nix(dev.name, request.POST['user'], request.POST['password'],
                             msg=request.POST['message'], reboot=reboot, timeout=timeout)
            else:
                shutdown_win(dev.name, request.POST['user'], request.POST['password'],
                             msg=request.POST['message'], reboot=reboot, timeout=timeout*60)
        except Exception as e:
            error_message = e.__unicode__()
            hf.save(dev, action, -1)
        finally:
            hf.save(dev, action, 0, request.POST['message'])
    last = History.objects.filter(device=device_id).latest()
    his = History.objects.filter(device=device_id)
    return render_to_response('bodhi/device.html',
                                {'device': dev,
                                'history' : his,
                                'latest' : last,
                                'error_message' : error_message})

def render_image(request, device_id):

  from cairoplot import CairoPlot
  import cairo
  import math
  import sys, io

  from bodhi.models import Device, History
  from django.db.models import Sum, Count
  from django.http import HttpResponse

  dev = Device.objects.get(pk=device_id)
  his = History.objects.filter(device=device_id, action=0).values('date').annotate(Count('result')).order_by('-date')[:10]
  h_labels = []
  data = {dev.name : []}
  colors = []
  for h in his :
    h_labels.append(h['date'].isoformat())
    data[dev.name].append(h['result__count'])
    if (h['result__count'] > 22) :
      color = (1,0,0)
    elif h['result__count'] > 12 :
      color = (1,1,0)
    elif h['result__count'] > 9 :
      color = (0.5,1,0)
    elif h['result__count'] > 6 :
      color = (0,1,0)
    elif h['result__count'] > 3 :
      color = (0,0.8,0.2)
    else :
      color = (0,0,1)
    colors.append(color)
        
  v_bounds = (0, 24)
  v_labels = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"]

  fo = io.BytesIO()
  surface = cairo.SVGSurface(fo, 600, 300)

  CairoPlot.bar_plot(surface, data, 600, 300, h_labels = h_labels, v_labels = v_labels, grid = True, rounded_corners = True, v_bounds = v_bounds, three_dimension = True, colors=colors)

  return HttpResponse(fo.getvalue(), mimetype='image/svg+xml')
