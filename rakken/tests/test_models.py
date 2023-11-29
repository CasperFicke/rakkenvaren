# rakken/test_models.py

# django
from django.test import TestCase

# local
from rakken.models import WaypointType

# tests
class WaypointTypeTestCase(TestCase):
  
  def setUp(self):
      WaypointType.objects.create(type="boei1", beschrijving="hele grote groene")
    
  def test_waypointtype_added(self):
    """Er kan een waypointtype worden toegevoegd"""
    nieuw = WaypointType.objects.get(type="boei1")
    # print (nieuw.beschrijving)
    self.assertEqual(nieuw.beschrijving, 'hele grote groene')