# rakken/views.py

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
from .models import Evenement, RakScore, Weer, Waypoint, Rak
from .utils import get_twa, get_score, get_bootje_coords

# Rakken indexpage
def index_rakken(request):
  title = 'index rakken'
  weer  = Weer.objects.first()
  context = {
    'title': title,
    'weer' : weer
  }
  return render(request, 'rakken/index_rakken.html', context)

# All waypoints
def all_waypoints(request):
  title           = 'waypoints'
  waypoints_list  = Waypoint.objects.all().order_by("naam")
  waypoints_count = waypoints_list.count()

  # Set up pagination
  paginator      = Paginator(waypoints_list, 25) # Show 25 waypoints per page.
  page_number    = request.GET.get('page')
  waypoints_page = paginator.get_page(page_number)
  page_count     = "a" * waypoints_page.paginator.num_pages
  is_paginated   = waypoints_page.has_other_pages
  context = {
    'title'          : title,
    'waypoints_list' : waypoints_list,
    'aantal'         : waypoints_count,
    'page_obj'       : waypoints_page,
    'is_paginated'   : is_paginated,
    'page_count'     : page_count
  }
  return render(request, 'rakken/all_waypoints.html', context)

# All rakken
def all_rakken(request):
  title        = 'rakken'
  rakken_list  = Rak.objects.all().order_by("evenement", "type")
  rakken_count = rakken_list.count()

  # Set up pagination
  paginator    = Paginator(rakken_list, 25) # Show 25 rakken per page.
  page_number  = request.GET.get('page')
  rakken_page  = paginator.get_page(page_number)
  page_count   = "a" * rakken_page.paginator.num_pages
  is_paginated = rakken_page.has_other_pages
  context = {
    'title'        : title,
    'rakken_list'  : rakken_list,
    'aantal'       : rakken_count,
    'page_obj'     : rakken_page,
    'is_paginated' : is_paginated,
    'page_count'   : page_count
  }
  return render(request, 'rakken/all_rakken.html', context)

# rakkenkaart
def rakkenkaart(request):
  title = 'rakkenkaart'
  context = {
    'title' : title,
  }
  tooltip = 'Click voor meer info'
  map = folium.Map(
    location   = [52.75, 5.0],
    tiles      = 'openstreetmap',
    zoom_start = 9
  )
  folium.TileLayer('openstreetmap').add_to(map)
  folium.TileLayer('CartoDB Positron').add_to(map)
  folium.TileLayer('CartoDB Dark_matter').add_to(map)
  folium.TileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
    name='openseamap',
    attr='openseamap'
  ).add_to(map)
  folium.TileLayer('https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0/Actueel_ortho25/EPSG:3857/{z}/{x}/{y}.jpeg',
    name='nlmaps luchtfoto',
    attr='nlmaps luchtfoto'
  ).add_to(map)
  folium.TileLayer('https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/standaard/EPSG:3857/{z}/{x}/{y}.png',
    name='nlmaps standaard',
    attr='nlmaps standaard'
  ).add_to(map)

  # add layer for waypoint markers
  waypointMarkersLayer = folium.FeatureGroup(name="Waypoints").add_to(map)
  # add layers fot rakkenlayers
  kz24uursLayer = folium.FeatureGroup(name="24uurs").add_to(map)
  kk8uursLayer  = folium.FeatureGroup(name="8uurs").add_to(map)
  folium.LayerControl().add_to(map)
  
  # Add waypoints uit de db
  waypoints            = Waypoint.objects.all()
  context['waypoints'] = waypoints
  df = pd.DataFrame(list(waypoints.values()))
  #print(df)
  for (index, rows) in df.iterrows():
    lat   = rows.loc['latitude']
    lng   = rows.loc['longitude']
    type  = rows.loc['type_id']
    popup = str(rows.loc['naam']+ ' ' + rows.loc['omschrijving'] + ' ' + str(type)).title()
    if type > 1:
      mc = 'green'
      mi = 'leaf'
    else:
      mc = 'red'
      mi = 'bolt'
    folium.Marker(
      location=[lat, lng],
      popup=popup,
      tooltip=tooltip,
      icon = folium.Icon(color=mc, prefix='fa', icon=mi)
    ).add_to(waypointMarkersLayer)

  # add polyline 24uurs
  rakken_list = Rak.objects.filter(evenement = 1)
  for rak in rakken_list:
    # set rak color
    if str(rak.type) == 'Baan-rak':
      color  = '#080080'
      dashed = '0'
    else:
      color  = 'green'
      dashed = '10'
    # set rak popup
    popup = folium.Popup(
      f'{rak.afstand} nm, van {rak.waypoint1} naar {rak.waypoint2}:{rak.bearing12} °, van {rak.waypoint2} naar {rak.waypoint1}: {rak.bearing21} °',
      min_width=150,
      max_width=300)
    # add line to layer
    folium.PolyLine([(rak.waypoint1.latitude, rak.waypoint1.longitude), (rak.waypoint2.latitude, rak.waypoint2.longitude)],
      popup      = popup,
      color      = color,
      dash_array = dashed,
      weight     = 4,
      ).add_to(kz24uursLayer)
    
  # add polyline 8uurs
  rakken_list = Rak.objects.filter(evenement = 2)
  for rak in rakken_list:
    # set rak color
    if str(rak.type) == 'Baan-rak':
      color = '#080080'
      dashed = '0'
    else:
      color = 'green'
      dashed = '10'
    # set rak popup
    popup = folium.Popup(
      f'{rak.afstand} nm, van {rak.waypoint1} naar {rak.waypoint2}:{rak.bearing12} °, van {rak.waypoint2} naar {rak.waypoint1}: {rak.bearing21} °',
      min_width=150,
      max_width=300)
    # add line to layer
    folium.PolyLine([(rak.waypoint1.latitude, rak.waypoint1.longitude), (rak.waypoint2.latitude, rak.waypoint2.longitude)],
      popup      = popup,
      color      = color,
      dash_array = dashed,
      weight     = 4,
      ).add_to(kk8uursLayer)
    
  # add fullscreen button to the map
  plugins.Fullscreen().add_to(map)
  # render map as html
  map = map._repr_html_()
  context['map'] = map
  return render(request, 'rakken/rakkenkaart.html', context)

# All rakscore
def all_rakscore(request):
  title       = 'rakscore'
  weer        = Weer.objects.first()
  rakken_list = Rak.objects.all()
  RakScore.objects.all().delete()
  # voor alle rakken in rakken_list
  for rak in rakken_list:
    # toevoegen: maak een twee rakscore records voor ieder rak. zowel voor de heen als voor de terugweg.
    # of door rakscore model aan te passen of door raknetwerk toe te voegen

    # bereken de rakscore per rak voor geselecteerde weer
    rakscore = RakScore(weer=weer, rak=rak)
    rakscore.waypoint1 = rak.waypoint1
    rakscore.waypoint2 = rak.waypoint2
    rakscore.bearing   = rak.bearing12
    rakscore.twa       = get_twa(weer.windrichting, rak.bearing12)
    rakscore.score     = get_score(rakscore.twa)[0]
    rakscore.color     = get_score(rakscore.twa)[1]
    rakscore.save()
    if str(rak.type) == "Baan-rak":
      rakscore = RakScore(weer=weer, rak=rak)
      rakscore.waypoint1 = rak.waypoint2
      rakscore.waypoint2 = rak.waypoint1
      rakscore.bearing   = rak.bearing21
      rakscore.twa       = get_twa(weer.windrichting, rak.bearing21)
      rakscore.score     = get_score(rakscore.twa)[0]
      rakscore.color     = get_score(rakscore.twa)[1]
      rakscore.save()
  rakscore_list  = RakScore.objects.all().order_by('rak', 'waypoint1')
  rakscore_count = rakscore_list.count()
  
  # Set up pagination
  paginator      = Paginator(rakscore_list, 25) # Show 25 rakken per page.
  page_number    = request.GET.get('page')
  rakscore_page  = paginator.get_page(page_number)
  page_count     = "a" * rakscore_page.paginator.num_pages
  is_paginated   = rakscore_page.has_other_pages
  context = {
    'title'         : title,
    'weer'          : weer,
    'rakken_list'   : rakken_list,
    'rakscore_list' : rakscore_list,
    'aantal'        : rakscore_count,
    'page_obj'      : rakscore_page,
    'is_paginated'  : is_paginated,
    'page_count'    : page_count
  }
  return render(request, 'rakken/all_rakscore.html', context)

# rakscorekaart
def rakscorekaart(request):
  title = 'rakscorekaart'
  weer  = Weer.objects.first()
  context = {
    'title' : title,
    'weer'  : weer
  }
  tooltip = 'Click voor meer info'
  map = folium.Map(
    location   = [52.75, 5.2],
    tiles      = 'openstreetmap',
    zoom_start = 9
  )
  folium.TileLayer('openstreetmap').add_to(map)
  folium.TileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
    name='openseamap',
    attr='openseamap'
  ).add_to(map)

  # add layer for waypoint markers
  waypointMarkersLayer = folium.FeatureGroup(name="Waypoints", show=False).add_to(map)
  # add layers fot rakkenlayers
  kz24uursLayer = folium.FeatureGroup(name="24uurs").add_to(map)
  kk8uursLayer  = folium.FeatureGroup(name="8uurs", show=False).add_to(map)
  folium.LayerControl().add_to(map)
  
  # Add waypoints uit de db
  waypoints            = Waypoint.objects.all()
  context['waypoints'] = waypoints
  df = pd.DataFrame(list(waypoints.values()))
  # print(df)
  for (index, rows) in df.iterrows():
    lat   = rows.loc['latitude']
    lng   = rows.loc['longitude']
    type  = rows.loc['type_id']
    popup = str(rows.loc['naam']+ ' ' + rows.loc['omschrijving']).title()
    if type > 1:
      mc = 'green'
      mi = 'leaf'
    else:
      mc = 'red'
      mi = 'bolt'
    folium.Marker(
      location = [lat, lng],
      popup    = popup,
      tooltip  = tooltip,
      icon     = folium.Icon(color=mc, prefix='fa', icon=mi)
    ).add_to(waypointMarkersLayer)

  # add polyline 24uurs
  rakscore_list = RakScore.objects.all()
  for rakscore in rakscore_list:
    # set linetype
    if str(rakscore.rak.type) == 'Baan-rak':
      dashed = '0'
    else:
      dashed = '10'
    # set rak color
    if str(rakscore.score) == 'slecht' or str(rakscore.score) == 'matig':
      color  = 'red'
    else:
      color  = 'green'
    # set rak popup
    popup = folium.Popup(
      f"{rakscore.waypoint1} to {rakscore.waypoint2}, distance: {rakscore.rak.afstand} nm, bearing: {rakscore.bearing} ° TWA: {rakscore.twa} ° rakscore {rakscore.score}",
      min_width = 150,
      max_width = 300)
    # add line to layer
    plugins.PolyLineOffset([(rakscore.waypoint1.latitude, rakscore.waypoint1.longitude), (rakscore.waypoint2.latitude, rakscore.waypoint2.longitude)],
      popup  = popup,
      color  = color,
      weight = 2,
      offset = 2,
      ).add_to(kz24uursLayer)
    # add boatmarker
    boot_pos = get_bootje_coords(rakscore.waypoint1.latitude, rakscore.waypoint1.longitude, rakscore.waypoint2.latitude, rakscore.waypoint2.longitude)
    plugins.BoatMarker(
      boot_pos,
      heading      = rakscore.bearing,
      wind_heading = rakscore.weer.windrichting,
      wind_speed   = rakscore.weer.windkracht,
      color        = color
      ).add_to(kz24uursLayer)


  # add polyline 8uurs
  rakscore_list = RakScore.objects.all()
  for rakscore in rakscore_list:
    # set rak color
    if str(rakscore.rak.type) == 'Baan-rak':
      color = '#080080'
      dashed = '0'
    else:
      color = 'green'
      dashed = '10'
    # set rak popup
    popup = folium.Popup(
      f'{rakscore.rak.afstand} nm, van {rakscore.rak.waypoint1} naar {rakscore.rak.waypoint2}:{rakscore.rak.bearing12} °, van {rakscore.rak.waypoint2} naar {rakscore.rak.waypoint1}: {rakscore.rak.bearing21} °',
      min_width=150,
      max_width=300)
    # add line to layer
    folium.PolyLine([(rakscore.rak.waypoint1.latitude, rakscore.rak.waypoint1.longitude), (rakscore.rak.waypoint2.latitude, rakscore.rak.waypoint2.longitude)],
      popup      = popup,
      color      = color,
      dash_array = dashed,
      weight     = 2,
      ).add_to(kk8uursLayer)
    # add boatmarker
    plugins.BoatMarker(
      (rakscore.waypoint1.latitude, rakscore.waypoint1.longitude),
      heading      = rakscore.rak.bearing12,
      wind_heading = rakscore.weer.windrichting,
      wind_speed   = rakscore.weer.windkracht,
      color="#8f8"
      ).add_to(kk8uursLayer)

  # add fullscreen button to the map
  plugins.Fullscreen().add_to(map)
  # render map as html
  map = map._repr_html_()
  context['map'] = map
  return render(request, 'rakken/rakscorekaart.html', context)
