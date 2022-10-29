# rakken/urls.py

# Django
from django.urls import path

# local
from . import views

app_name = "rakken"

urlpatterns = [
  # Rakken
  path('rakken/'               , views.index_rakken, name="index-rakken"),
  path('rakken/waypoints/'     , views.all_waypoints, name="all-waypoints"),
  path('rakken/rakken/'        , views.all_rakken, name="all-rakken"),
  path('rakken/rakkenkaart/'   , views.rakkenkaart, name="rakkenkaart"),
  path('rakken/rakscore/'      , views.all_rakscore, name="all-rakscore"),
  path('rakken/rakscorekaart/' , views.rakscorekaart, name="rakscorekaart"),
]