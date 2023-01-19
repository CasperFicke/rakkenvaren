# site_basis/views.py

from django.shortcuts import render
from django.views import generic

# home view
class HomeView(generic.TemplateView):
	"""
    Website home page.

    **Template:**

    :template:`site_basis/index.html`
    """
	template_name = "site_basis/index.html"

# about view
class AboutView(generic.TemplateView):
	"""
    Website about page.

    **Template:**

    :template:`site_basis/about.html`
    """
	template_name = "site_basis/about.html"


