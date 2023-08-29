# rakken.utils.py

from django.contrib.gis.geoip2 import GeoIP2

# helper functions

# calculate twa
def get_twa(windrichting, bearing):
  if abs(windrichting - bearing) <= 180:
    twa = round(abs(windrichting - bearing), 0)
  elif 360 - bearing < 180:
    twa = round(360 + windrichting - bearing, 0)
  else:
    twa = round(360 - windrichting + bearing, 0)
  return twa

# method to calculate score
def get_score(twa):
  if twa <= 45:
    score = 'slecht'
    color = 'table-danger'
  elif twa <= 70:
    score = 'matig'
    color = 'table-warning'
  elif twa <= 100:
    score = 'goed'
    color = 'table-success'
  elif twa <= 140:
    score = 'zeer goed'
    color = 'bg-success'
  elif twa <= 160:
    score = 'goed'
    color = 'table-success'
  else:
    score = 'redelijk'
    color = 'table-secondary'
  return score, color

# bepaal positie vh bootje
def get_bootje_coords(wp1_lat, wp1_lon, wp2_lat, wp2_lon):
  cord = [(3*wp1_lat+wp2_lat)/4, (3*wp1_lon+wp2_lon)/4]
  return cord

# get ip adres
def get_ip_address(request):
  x_forwarded_for =request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return ip

# get geo data voor een IP adres
def get_geo(ip):
  g        = GeoIP2()
  country  = g.country(ip)
  city     = g.city(ip)
  lat, lon = g.lat_lon(ip)
  return country, city, lat, lon

# bepaal center
def get_center_coords(latA, lonA, latB=None, lonB=None):
  cord = (latA, lonA)
  if latB:
    cord = [(latA+latB)/2, (lonA+lonB)/2]
  return cord

# bepaal zoom
def get_zoom(distance):
  if distance <= 6:
    return 11
  elif distance > 6 and distance <= 10:
    return 10
  elif distance > 10 and distance <= 20:
    return 10
  elif distance > 20 and distance <= 50:
    return 6
  else:
    return 4
  
