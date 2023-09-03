# rakken/urls.py

# Django
from django.urls import path

# local
from . import views
from .views import (
  WaypointCreateView, 
  WaypointUpdateView,
  WaypointDeleteView,
  RakCreateView,
  RakUpdateView,
  RakDeleteView
  )

app_name = "rakken"

urlpatterns = [
  # Waypoints
  path('waypoints/'                , views.all_waypoints, name="all-waypoints"),
  path('waypointsjson/'            , views.all_waypointsjson, name="all-waypointsjson"),
  # CRUD single waypoint
  path('waypoints/add'             , WaypointCreateView.as_view(), name="add-waypoint"),
  path('waypoints/<waypoint_uuid>' , views.show_waypoint, name="show-waypoint"),
  path('waypoints/<int:pk>/update' , WaypointUpdateView.as_view(), name="update-waypoint"),
  path('waypoints/<int:pk>/delete' , WaypointDeleteView.as_view(), name="delete-waypoint"),

  # Rakken
  path('rakken/'               , views.index_rakken, name="index-rakken"),
  path('rakken/rakken/'        , views.all_rakken, name="all-rakken"),
  path('rakken/rakkenkaart/'   , views.rakkenkaart, name="rakkenkaart"),
  path('rakken/rakkengraph/'   , views.rakkengraph, name="rakkengraph"),
  # CRUD single rak
  #path('rakken/<int:pk>'        , RakDetailView.as_view(), name="show-rak"),
  path('rakken/add'             , RakCreateView.as_view(), name="add-rak"),
  path('rakken/<rak_uuid>'      , views.show_rak, name="show-rak"),
  path('rakken/<int:pk>/update' , RakUpdateView.as_view(), name="update-rak"),
  path('rakken/<int:pk>/delete' , RakDeleteView.as_view(), name="delete-rak"),
  # Rak scores
  path('rakken/rakscore/'           , views.all_rakscore, name="all-rakscore"),
  path('rakken/rakscore/csv/'       , views.csv_rakscores, name="csv_rakscores"),
  path('rakken/rakscore/pdf/'       , views.pdf_rakscores, name="pdf_rakscores"),
  path('rakken/rakscorekaart/'      , views.rakscorekaart, name="rakscorekaart"),
  path('rakken/rakscorekaart/8uurs' , views.rakscorekaart8uurs, name="rakscorekaart8uurs"),
]