# boten/urls.py

# django
from django.urls import path

# local
from . import views

app_name = "boten"

urlpatterns = [
  # boten
  path('boten/'             , views.all_boten, name="all-boten"),
  path('boten/<boot_uuid>'  , views.show_boot, name="show-boot"),
]