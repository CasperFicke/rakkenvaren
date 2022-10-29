# rakken.utils.py

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