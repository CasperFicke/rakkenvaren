# site_basis/urls.py

# django
from django.urls import path

# local
from . import views

app_name = "site_basis"

urlpatterns = [
	path("", views.HomeView.as_view(), name="home"),
	path('about', views.AboutView.as_view(), name="about"),
	path('contact', views.ContactView.as_view(), name="contact"),
	path('privacy', views.PrivacyView.as_view(), name="privacy"),
]