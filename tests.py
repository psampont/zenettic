#!/usr/bin/python
from cairoplot import CairoPlot
import cairo
import math
import sys

from django.core.management import setup_environ
import settings
setup_environ(settings)

from bodhi.models import Device, History
from django.db.models import Sum, Count

device_id = 149
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
        
#Dot Line Plot
#print(h_labels)
#print(data)
v_bounds = (0, 24)
v_labels = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"]

#fo = file('test.svg', 'w')
surface = cairo.SVGSurface(sys.stdout, 600, 300)

CairoPlot.bar_plot(surface, data, 600, 300, h_labels = h_labels, v_labels = v_labels, grid = True, rounded_corners = True, v_bounds = v_bounds, three_dimension = True, colors=colors)


