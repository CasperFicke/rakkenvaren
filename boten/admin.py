# boten/admin.py

# django
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# local
from .models import (
  Boot,
  PolarpuntType,
  Polarpunt
  )

# Register Polarpunttype
class PolarpuntTypeAdmin(admin.ModelAdmin):
  list_display = ('type', 'beschrijving',)
  ordering     = ('type',)
# overall admin area
admin.site.register(PolarpuntType, PolarpuntTypeAdmin)

# Register Polarpunt
class PolarpuntAdmin(ImportExportModelAdmin):
  fields       = ('windspeed', 'twa', 'boatspeed', 'vmg')
  list_display = ('boot', 'windspeed', 'twa', 'boatspeed', 'type')
  ordering     = ('boot', 'windspeed', 'twa',)
# overall admin area
admin.site.register(Polarpunt, PolarpuntAdmin)

# create inline for polarpoint
class PolarpuntInline(admin.TabularInline):
  model  = Polarpunt
  fields = ('type', 'windspeed', 'twa', 'boatspeed', 'vmg')
  extra  = 0

# Register Boot
class BootAdmin(ImportExportModelAdmin):
  list_display = ('naam', 'model', 'gph', 'toelichting',)
  ordering     = ('naam',)
  inlines      = [PolarpuntInline]
# overall admin area
admin.site.register(Boot, BootAdmin)
