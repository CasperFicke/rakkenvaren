# rakken/tests/test_urls.py

# django
from django.test import SimpleTestCase
from django.urls import reverse, resolve

# local
from rakken.views import all_waypoints

# Tests
class TestUrls(SimpleTestCase):

  # all-waypoints url
  def test_allwappoints_url_resolves(self):
    url = reverse('rakken:all-waypoints')
    #print (resolve(url))
    self.assertEquals(resolve(url).func , all_waypoints)
