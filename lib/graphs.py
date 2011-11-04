#!/usr/bin/python
""" Generic graph """

__docformat__ = 'epytext en'

######################################################################
## Imports
######################################################################
import io
import cairo
from cairoplot import CairoPlot
from bodhi.models import Device, History

######################################################################
##
######################################################################

def history_img(device_id, days):
  '''
  Create a SVG image from the history of device_id device
  '''

  dev = Device.objects.get(pk=device_id)
  his = History.objects.filter(device=device_id, action=0, user="cron", result=0).values('date').annotate(Count('result')).order_by('-date')[:days]

  h_labels = []
  data = {dev.name : []}
  colors = []
  for h in his :
    h_labels.append(h['date'].isoformat()[5:])
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
  surface = cairo.SVGSurface(fo, int(days)*30, 300)

  CairoPlot.bar_plot(surface, data, int(days)*30, 300, h_labels = h_labels, v_labels = v_labels, grid = True, rounded_corners = True, v_bounds = v_bounds, three_dimension = False, colors=colors)

  return fo.getvalue()
