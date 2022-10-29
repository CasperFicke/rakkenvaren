# boten/views.py

# django
from django.shortcuts import render
from django.core.paginator import Page, Paginator
from django.http import HttpResponse, HttpResponseRedirect, Http404

from geopy.distance  import geodesic
from geographiclib.geodesic import Geodesic

#import numpy and matplotlib library
import numpy as np
import matplotlib.pyplot as plt

# import io
from io import StringIO
import urllib, base64

geod = Geodesic.WGS84

# import pandas (data-analytics)
import pandas as pd

import folium
from folium import plugins

# local
from .models import Boot

# All boten
def all_boten(request):
  title        = 'boten'
  boten_list  = Boot.objects.all().order_by("naam", "gph")
  boten_count = boten_list.count()
   
  # Set up pagination
  paginator    = Paginator(boten_list, 25) # Show 25 rakken per page.
  page_number  = request.GET.get('page')
  boten_page  = paginator.get_page(page_number)
  page_count   = "a" * boten_page.paginator.num_pages
  is_paginated = boten_page.has_other_pages
  context = {
    'title'        : title,
    'boten_list'   : boten_list,
    'aantal'       : boten_count,
    'page_obj'     : boten_page,
    'is_paginated' : is_paginated,
    'page_count'   : page_count
  }
  return render(request, 'boten/all_boten.html', context)

# show boot
def show_boot(request, boot_uuid):
  try:
    boot    = Boot.objects.get(uuid=boot_uuid)
    title   = 'boot: ' + boot.naam
    # plot sinus
    x = np.arange(0,np.pi*3,.1)
    y = np.sin(x)
    fig = plt.figure()
    plt.plot(x,y)
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()

    # plot cardiod
    fig = plt.figure()
    fig.add_subplot(111, projection='polar')
    # Set the title of the polar plot
    plt.title('Cardioid in polar format:radius = a + (b*sin(k*radian))')
    # Radian values upto 2*pi
    rads = np.arange(0, (2*np.pi), 0.01)
    a = 1
    b = 1
    k = 1
    # a = -1 and b = -1
    for radian in rads:
      radius = a + (b*np.sin(k*radian))
      # Plot the cardioid in polar co-ordinates
      plt.polar(radian, radius, 'v')
    # Display the cardioid
    plt.show()
    
    # plot polar
    fig = plt.figure()
    fig.add_subplot(111, projection='polar')
    # Set the title of the polar plot
    plt.title('Polar van de boot')
    # Radian values upto 2*pi
    rads = np.arange(0, (2*np.pi), 0.01)
    a = 1
    b = 1
    k = 1
    # a = -1 and b = -1
    for polarpunt in boot.polarpunten.all():
      twa= polarpunt.twa
      bootsnelheid = polarpunt.boatspeed
      #bootsnelheid = polarpunt.boatspeed.filter(windspeed=20)
      # Plot the polarpoints in polar co-ordinates
      plt.polar(twa, bootsnelheid, 'v')
    # Display the polar
    plt.show()

    context = {
      'title' : title,
      'boot'  : boot,
      'data'  : data,
    }
    return render(request, 'boten/show_boot.html', context)
  except:
    raise Http404()
