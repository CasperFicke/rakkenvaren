# rakken/views.py

# django
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Page, Paginator
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse, FileResponse
from django.core import serializers

from geopy.distance  import geodesic
from geographiclib.geodesic import Geodesic

# import numpy and matplotlib
import numpy as np
import matplotlib
matplotlib.use('agg')

# import io
import io
from io import StringIO
import urllib, base64
import csv

# pdf creation with reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4

geod = Geodesic.WGS84

# import pandas (data-analytics)
import pandas as pd

# import networkx (network analysis)
import networkx as nx

# import folium kaarten
import folium
from folium import plugins

from datetime import datetime, timedelta, date

# local
from .models import Evenement, RakScore, Weer, Waypoint, Rak
from .utils import get_twa, get_score, get_bootje_coords, get_ip_address, get_center_coords, get_zoom

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

# All waypoints json
def all_waypointsjson(request):
  waypoints_list  = Waypoint.objects.all().order_by("naam")
  data = serializers.serialize("json", waypoints_list, fields=('naam', 'latitude', 'longitude'))
  return JsonResponse(data, safe=False)

# show waypoint
def show_waypoint(request, waypoint_uuid):
  try:
    waypoint = Waypoint.objects.get(uuid=waypoint_uuid)
    title    = 'waypoint: ' + waypoint.naam
    loca     = waypoint.latitude, waypoint.longitude
    # map setup
    m = folium.Map(
      location   = loca,
      tiles      = 'openstreetmap',
      zoom_start = 12
    )
    folium.TileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
      name = 'openseamap',
      attr = 'openseamap'
    ).add_to(m)

    # custom icon    
    url          = "https://leafletjs.com/examples/custom-icons/{}".format
    icon_image   = url("leaf-red.png")
    shadow_image = url("leaf-shadow.png")
    icon = folium.CustomIcon(
      icon_image,                   # image of the icon
      shadow_image  = shadow_image, # image of the shadow
      icon_size     = (38, 95),     # size of the icon
      shadow_size   = (50, 64),     # size of the shadow
      icon_anchor   = (22, 94),     # point of the icon which will correspond to marker's location
      shadow_anchor = (4, 62),      # the same for the shadow
      popup_anchor  = (-3, -76),    # point from which the popup should open relative to the iconAnchor
    )
    # add location marker
    folium.Marker(
      location = loca,
      icon     = icon,
      tooltip  = waypoint.naam,
      popup    = waypoint.omschrijving,
    ).add_to(m)

    # add layercontrol to the map
    folium.LayerControl().add_to(m)
    # convert map fir html representation
    m = m._repr_html_()
    context  = {
      'title'    : title,
      'waypoint' : waypoint,
      'm'        : m
    }
    return render(request, 'rakken/show_waypoint.html', context)
  except:
    raise Http404()

# Add waypoint
class WaypointCreateView(CreateView):
  model         = Waypoint
  template_name = 'rakken/waypointform.html'
  fields        = ['naam', 'omschrijving', 'latitude', 'longitude', 'type']
  success_url   = reverse_lazy('rakken:all-waypoints')

# Update waypoint
class WaypointUpdateView(UpdateView):
  model         = Waypoint
  template_name = 'rakken/waypointform.html'
  fields        = ['naam', 'omschrijving', 'latitude', 'longitude', 'type']

# Delete waypoint
class WaypointDeleteView(DeleteView):
  model         = Waypoint
  template_name = 'rakken/waypoint_confirm_delete.html'
  success_url   = reverse_lazy('rakken:all-waypoints')

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

# show rak
def show_rak(request, rak_uuid):
  try:
    rak = Rak.objects.get(uuid=rak_uuid)
    title   = 'rak '
    tooltip = 'Click voor meer info'
    loca    = rak.waypoint1.latitude, rak.waypoint1.longitude
    locb    = rak.waypoint2.latitude, rak.waypoint2.longitude

    # Map setup
    m = folium.Map(
      location   = get_center_coords(rak.waypoint1.latitude, rak.waypoint1.longitude, rak.waypoint2.latitude, rak.waypoint2.longitude),
      tiles      = 'openstreetmap',
      zoom_start = get_zoom(rak.afstand), # helperfunction uit utils.py
      #zoom_start = 10
    )
    folium.TileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
      name='openseamap',
      attr='openseamap'
    ).add_to(m)
    # add layer for waypoints
    waypointsLayer = folium.FeatureGroup(name="Waypoints").add_to(m)
    # add layer for rak
    rakLayer = folium.FeatureGroup(name="Rak").add_to(m)

    # add waypoint1
    folium.Marker(
      location = loca,
      tooltip  = rak.waypoint1.naam,
      popup    = rak.waypoint1.omschrijving,
      icon     = folium.Icon(color='blue')
    ).add_to(waypointsLayer)

    # add waypoint2
    folium.Marker(
      location = locb,
      tooltip  = rak.waypoint2.naam,
      popup    = rak.waypoint2.omschrijving,
      icon     = folium.Icon(color='blue')
    ).add_to(waypointsLayer)

    # add polyline
    folium.PolyLine(
      [loca, locb],
      popup   = str(rak.waypoint1.naam) + ' - ' + str(rak.waypoint2.naam),
      tooltip = tooltip,
      color   = '#080080',
      weight  = 4,
    ).add_to(rakLayer)

    # layercontrol
    folium.LayerControl().add_to(m)

    m = m._repr_html_()
    context  = {
      'title' : title,
      'rak'   : rak,
      'm'     : m
    }
    return render(request, 'rakken/show_rak.html', context)
  except:
    raise Http404()

# Add Rak
class RakCreateView(CreateView):
  model         = Rak
  template_name = 'rakken/rakform.html'
  fields        = ['evenement', 'waypoint1', 'waypoint2', 'type', 'lengte']
  success_url   = reverse_lazy('rakken:all-rakken')

# Update Rak
class RakUpdateView(UpdateView):
  model         = Rak
  template_name = 'rakken/rakform.html'
  fields        = ['evenement', 'waypoint1', 'waypoint2', 'type', 'lengte']

# Delete rak
class RakDeleteView(DeleteView):
  model         = Rak
  template_name = 'rakken/rak_confirm_delete.html'
  success_url   = reverse_lazy('rakken:all-rakken')

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
    lat     = rows.loc['latitude']
    lng     = rows.loc['longitude']
    type    = rows.loc['type_id']
    tooltip = rows.loc['naam']
    popup   = str(rows.loc['omschrijving'] + ' ' + str(type)).title()
    #popup  = str(rows.loc['naam']+ ' ' + rows.loc['omschrijving'] + ' ' + str(type)).title()
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

# export rakscores to CSV
def csv_rakscores(request):
  response= HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename=RakscoreList_' + str(date.today()) + '.csv'
  # create CSV writer
  writer=csv.writer(response)
  # Select all rakscors to export
  rakscore_list = RakScore.objects.all()
  # create first row with column headings
  writer.writerow(['Evenement', 'Rak-type', 'Waypoint1', 'Waypoint2', 'Lengte', 'Bearing', 'Windrichting', 'TWA', 'score'])
  # loop thru and output
  for rakscore in rakscore_list:
    writer.writerow([
      rakscore.rak.evenement,
      rakscore.rak.type,
      rakscore.waypoint1,
      rakscore.waypoint2,
      rakscore.rak.lengte,
      rakscore.bearing,
      rakscore.weer.windrichting,
      rakscore.twa,
      rakscore.score
    ])
  return response

# export rakscores to PDF
def pdf_rakscores(request):
  # Create a file-like buffer to receive PDF data.
  buffer = io.BytesIO()
  # Create the PDF object, using the buffer as its "file."
  p = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
  # Create a textobject
  texobj = p.beginText()
  texobj.setTextOrigin(cm, cm)
  texobj.setFont("Helvetica", 14)

  rakscore_list = RakScore.objects.all()
  # create empty list
  lines = []
  # loop thru to build contentlist
  for rakscore in rakscore_list:
    lines.append('van ' + str(rakscore.waypoint1) + ' naar ' + str(rakscore.waypoint2) + ' is koers ' + str(rakscore.bearing)),
    lines.append('  ')
  # loop thru and output
  for line in lines:
    texobj.textLine(line)
  # finish pdf
  p.drawText(texobj)
  p.showPage()
  p.save()
  buffer.seek(0)
  # return pdf
  return FileResponse(buffer, as_attachment=True, filename='RakscoreList_' + str(date.today()) + '.pdf')

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
    lat     = rows.loc['latitude']
    lng     = rows.loc['longitude']
    type    = rows.loc['type_id']
    tooltip = rows.loc['naam']
    popup   = rows.loc['omschrijving']
    #popup = str(rows.loc['naam']+ ' ' + rows.loc['omschrijving']).title()
    if type > 1:
      mc = 'green'
      mi = 'leaf'
    else:
      mc = 'red'
      mi = 'bolt'
    folium.Marker(
      location = [lat, lng],
      tooltip  = tooltip,
      popup    = popup,
      icon     = folium.Icon(color=mc, prefix='fa', icon=mi)
    ).add_to(waypointMarkersLayer)

  rakscore_list = RakScore.objects.all()
  # add polyline 24uurs
  for rakscore in rakscore_list:
    if rakscore.rak.evenement_id == 1:
      # set linetype
      if str(rakscore.rak.type) == 'Baan-rak':
        dashed = '0'
      else:
        dashed = '10'
      # set rak color
      if str(rakscore.score) == 'slecht':
        color  = 'red'
      elif str(rakscore.score) == 'matig':
        color  = 'orange'
      elif str(rakscore.score) == 'goed':
        color  = 'green'
      elif str(rakscore.score) == 'zeer goed':
        color  = 'pink'
      elif str(rakscore.score) == 'redelijk':
        color  = 'purple'
      else:
        color  = 'white'
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
  for rakscore in rakscore_list:
    if rakscore.rak.evenement_id == 2:
      # set rak color
      if str(rakscore.rak.type) == 'Baan-rak':
        dashed = '0'
      else:
        dashed = '10'
      # set rak color
      if str(rakscore.score) == 'slecht':
        color  = 'red'
      elif str(rakscore.score) == 'matig':
        color  = 'orange'
      elif str(rakscore.score) == 'goed':
        color  = 'green'
      elif str(rakscore.score) == 'zeer goed':
        color  = 'pink'
      elif str(rakscore.score) == 'redelijk':
        color  = 'purple'
      else:
        color  = 'white'
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
        ).add_to(kk8uursLayer)
      # add boatmarker
      boot_pos = get_bootje_coords(rakscore.waypoint1.latitude, rakscore.waypoint1.longitude, rakscore.waypoint2.latitude, rakscore.waypoint2.longitude)
      plugins.BoatMarker(
        boot_pos,
        heading      = rakscore.bearing,
        wind_heading = rakscore.weer.windrichting,
        wind_speed   = rakscore.weer.windkracht,
        color        = color
        ).add_to(kk8uursLayer)

  # add fullscreen button to the map
  plugins.Fullscreen().add_to(map)
  # render map as html
  map = map._repr_html_()
  context['map'] = map
  return render(request, 'rakken/rakscorekaart.html', context)

# rakscorekaart 8uurs
def rakscorekaart8uurs(request):
  title = 'rakscorekaart 8uurs'
  weer  = Weer.objects.first()
  context = {
    'title' : title,
    'weer'  : weer
  }
  tooltip = 'Click voor meer info'
  map = folium.Map(
    location   = [52.54, 5.2],
    tiles      = 'openstreetmap',
    zoom_start = 11
  )
  folium.TileLayer('openstreetmap').add_to(map)
  folium.TileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
    name='openseamap',
    attr='openseamap'
  ).add_to(map)

  # add layer for waypoint markers
  waypointMarkersLayer = folium.FeatureGroup(name="Waypoints", show=False).add_to(map)
  # add layers fot scores
  slechtLayer   = folium.FeatureGroup(name="slecht - 0 < twa < 45", show=False).add_to(map)
  matigLayer    = folium.FeatureGroup(name="matig - 45 < twa > 100", show=False).add_to(map)
  goedLayer     = folium.FeatureGroup(name="goed - 100 < twa > 140").add_to(map)
  zeergoedLayer = folium.FeatureGroup(name="zeer goed - 140 < twa > 160").add_to(map)
  redelijkLayer = folium.FeatureGroup(name="redelijk - 160 < twa > 180").add_to(map)
  folium.LayerControl().add_to(map)
  
  # Add waypoints uit de db
  waypoints            = Waypoint.objects.all()
  context['waypoints'] = waypoints
  df = pd.DataFrame(list(waypoints.values()))
  # print(df)
  for (index, rows) in df.iterrows():
    lat     = rows.loc['latitude']
    lng     = rows.loc['longitude']
    type    = rows.loc['type_id']
    tooltip = rows.loc['naam']
    popup   = rows.loc['omschrijving']
    #popup = str(rows.loc['naam']+ ' ' + rows.loc['omschrijving']).title()
    if type > 1:
      mc = 'green'
      mi = 'leaf'
    else:
      mc = 'red'
      mi = 'bolt'
    folium.Marker(
      location = [lat, lng],
      tooltip  = tooltip,
      popup    = popup,
      icon     = folium.Icon(color=mc, prefix='fa', icon=mi)
    ).add_to(waypointMarkersLayer)
  
  rakscore_list = RakScore.objects.all()
  # add polyline 8uurs
  for rakscore in rakscore_list:
    if rakscore.rak.evenement_id == 2:
      # set rak color
      if str(rakscore.rak.type) == 'Baan-rak':
        dashed = '0'
      else:
        dashed = '10'
      # set rak color
      if str(rakscore.score) == 'slecht':
        color  = 'red'
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
          ).add_to(slechtLayer)
        # add boatmarker
        boot_pos = get_bootje_coords(rakscore.waypoint1.latitude, rakscore.waypoint1.longitude, rakscore.waypoint2.latitude, rakscore.waypoint2.longitude)
        plugins.BoatMarker(
          boot_pos,
          heading      = rakscore.bearing,
          wind_heading = rakscore.weer.windrichting,
          wind_speed   = rakscore.weer.windkracht,
          color        = color
          ).add_to(slechtLayer)
      elif str(rakscore.score) == 'matig':
        color  = 'orange'
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
          ).add_to(matigLayer)
        # add boatmarker
        boot_pos = get_bootje_coords(rakscore.waypoint1.latitude, rakscore.waypoint1.longitude, rakscore.waypoint2.latitude, rakscore.waypoint2.longitude)
        plugins.BoatMarker(
          boot_pos,
          heading      = rakscore.bearing,
          wind_heading = rakscore.weer.windrichting,
          wind_speed   = rakscore.weer.windkracht,
          color        = color
          ).add_to(matigLayer)
      elif str(rakscore.score) == 'goed':
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
          ).add_to(goedLayer)
        # add boatmarker
        boot_pos = get_bootje_coords(rakscore.waypoint1.latitude, rakscore.waypoint1.longitude, rakscore.waypoint2.latitude, rakscore.waypoint2.longitude)
        plugins.BoatMarker(
          boot_pos,
          heading      = rakscore.bearing,
          wind_heading = rakscore.weer.windrichting,
          wind_speed   = rakscore.weer.windkracht,
          color        = color
          ).add_to(goedLayer)
      elif str(rakscore.score) == 'zeer goed':
        color  = 'purple'
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
          ).add_to(zeergoedLayer)
        # add boatmarker
        boot_pos = get_bootje_coords(rakscore.waypoint1.latitude, rakscore.waypoint1.longitude, rakscore.waypoint2.latitude, rakscore.waypoint2.longitude)
        plugins.BoatMarker(
          boot_pos,
          heading      = rakscore.bearing,
          wind_heading = rakscore.weer.windrichting,
          wind_speed   = rakscore.weer.windkracht,
          color        = color
          ).add_to(zeergoedLayer)
      elif str(rakscore.score) == 'redelijk':
        color  = 'blue'
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
          ).add_to(redelijkLayer)
        # add boatmarker
        boot_pos = get_bootje_coords(rakscore.waypoint1.latitude, rakscore.waypoint1.longitude, rakscore.waypoint2.latitude, rakscore.waypoint2.longitude)
        plugins.BoatMarker(
          boot_pos,
          heading      = rakscore.bearing,
          wind_heading = rakscore.weer.windrichting,
          wind_speed   = rakscore.weer.windkracht,
          color        = color
          ).add_to(redelijkLayer)
      else:
        color  = 'white'

  # add fullscreen button to the map
  plugins.Fullscreen().add_to(map)
  # render map as html
  map = map._repr_html_()
  context['map'] = map
  return render(request, 'rakken/rakscorekaart.html', context)

# rakkengraph
def rakkengraph(request):
  title      = 'rakkengraph'
  # bepaal rakken en waypoints die in graph moeten worden opgenomen
  rakken = Rak.objects.filter(evenement=2)
  
  # bepaal unieke waypoints behorende bij rakken van geselecteerd evenement
  usedwaypoints = []
  for rak in rakken:
    if not rak.waypoint1 in usedwaypoints:
      usedwaypoints.append(rak.waypoint1)
    if not rak.waypoint2 in usedwaypoints:
      usedwaypoints.append(rak.waypoint2)
  
  # define graph
  G = nx.Graph(name="8 uurs")
  #G.clear()

  # Add waypoints as nodes
  for waypoint in usedwaypoints:
    G.add_node(waypoint.naam, type=waypoint.type.type)
  
  # Add rakken as edges
  dfrakken = pd.DataFrame(list(rakken.values()))
  #print(dfrakken)
  for (index, rows) in dfrakken.iterrows():
    wpa = Waypoint.objects.filter(pk=rows.loc['waypoint1_id'])
    wpb = Waypoint.objects.filter(pk=rows.loc['waypoint2_id'])
    G.add_edge(wpa[0].naam, wpb[0].naam, lengte=rows.loc['lengte'])

  #print(G.nodes(data=True))
  #print(G.edges(data=True))
  #print(G.edges["Hoorn", "SH2"])
  #print(G.graph)
  aantalnodes = G.number_of_nodes()
  aantaledges = G.number_of_edges()

  nx.draw(
    G,
    with_labels = True,
    node_color  = "teal",
    node_size   = 2000,
    font_color  = "black",           # node textcolor
    font_size   = 14,                # node fontsize
    font_family = "Times New Roman", # node font
    font_weight = "normal",          # nodetext fontweight
    width       = 3                  # edge line width
  )
  # set margin om graph picture
  matplotlib.pyplot.margins(0.2)
  
  # convert graph picture into string buffer and then convert base64 code into image
  buf = io.BytesIO()
  matplotlib.pyplot.savefig(buf, format='png')
  buf.seek(0)
  string = base64.b64encode(buf.read())
  uri    = urllib.parse.quote(string)

  context = {
    'title'       : title,
    'data'        : uri,
    'graphnaam'   : G.name,
    'aantalnodes' : aantalnodes,
    'aantaledges' : aantaledges
  }
  return render(request, 'rakken/rakkengraph.html', context)