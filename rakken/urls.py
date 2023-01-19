# rakken/urls.py

# Django
from django.urls import path

# local
from . import views
from .views import WaypointDetailView, WaypointCreateView, WaypointUpdateView, WaypointDeleteView

app_name = "rakken"

urlpatterns = [
  # Waypoints
  path('waypoints/'                , views.all_waypoints, name="all-waypoints"),
  path('waypoints/<int:pk>'        , WaypointDetailView.as_view(), name="show-waypoint"),
  path('waypoints/add'             , WaypointCreateView.as_view(), name="add-waypoint"),
  path('waypoints/<int:pk>/update' , WaypointUpdateView.as_view(), name="update-waypoint"),
  path('waypoints/<int:pk>/delete' , WaypointDeleteView.as_view(), name="delete-waypoint"),

  # Rakken
  path('rakken/'               , views.index_rakken, name="index-rakken"),
  path('rakken/rakken/'        , views.all_rakken, name="all-rakken"),
  path('rakken/rakkenkaart/'   , views.rakkenkaart, name="rakkenkaart"),
  path('rakken/rakscore/'      , views.all_rakscore, name="all-rakscore"),
  path('rakken/rakscorekaart/' , views.rakscorekaart, name="rakscorekaart"),
]