# site_basis/views.py

from django.shortcuts import render
from django.views import generic

# home view
# classbased view 
class HomeView(generic.TemplateView):
	"""
    Website home page.

    **Template:**

    :template:`site_basis/index.html`
    """
	template_name = "site_basis/index.html"


