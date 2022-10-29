# boten/models.py

# django
from django.urls import reverse
from django.db import models

# installed packages
import uuid

# abstracts from django extensions
from django_extensions.db.models import (
  TimeStampedModel,
	ActivatorModel 
)
  
# Boot model
class Boot(TimeStampedModel,ActivatorModel,models.Model):
  class Meta:
    verbose_name        = 'boot'
    verbose_name_plural = 'boten'
    ordering            = ['naam']
  # attributes
  naam         = models.CharField('Naam', max_length=255, help_text='Naam van de boot')
  model        = models.CharField('Model', blank=True, max_length=255, help_text='Model boot')
  toelichting  = models.TextField('Toelichting', blank=True, help_text='Toelichting bij deze boot')
  gph          = models.FloatField('GPH', blank=True, null=True, help_text='GPH van deze boot')
  # secundair
  uuid         = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, help_text='Unique identifier (UUID4)')
   
  def get_absolute_url(self):
    return reverse("boten:show-boot", args=[self.uuid])

  # functie om model in de admin web-pagina te kunnen presenteren
  def __str__(self):
    return self.naam

# Polarpuntype model
class PolarpuntType(TimeStampedModel,ActivatorModel,models.Model):
  class Meta:
    verbose_name        = 'polarpunt type'
    verbose_name_plural = 'polarpunt types'
    ordering            = ['type']
  # attributes
  type         = models.CharField('Polarpunt Type', max_length=100)
  beschrijving = models.TextField('Beschrijving', blank=True)
  # secundair
  uuid         = models.UUIDField(unique=True, default=uuid.uuid4, help_text='Unique identifier (UUID4)')
  
  # functie om model in de admin web-pagina te kunnen presenteren
  def __str__(self):
    return self.type

# Polarpunt model
class Polarpunt(TimeStampedModel,ActivatorModel,models.Model):
  class Meta:
    verbose_name        = 'polarpunt'
    verbose_name_plural = 'polarpunten'
  # attributes
  windspeed = models.PositiveIntegerField('windspeed')
  twa       = models.FloatField('ware windhoek', default=0)
  boatspeed = models.FloatField('predicted boatspeed', blank=True, null=True)
  vmg       = models.FloatField('predicted VMG', blank=True, null=True)
  # relaties
  type      = models.ForeignKey(PolarpuntType, blank=True, null=True, on_delete=models.SET_NULL, related_name='polarpunten')
  boot      = models.ForeignKey(Boot, null=True, on_delete=models.CASCADE, related_name='polarpunten')
  # secundair
  uuid      = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, help_text='Unique identifier (UUID4)')

  # functie om model in de admin web-pagina te kunnen presenteren
  def __str__(self):
    return f'{self.boot.naam} - tws: {self.windspeed} - twa: {self.twa} - boatspeed: {self.boatspeed}'
