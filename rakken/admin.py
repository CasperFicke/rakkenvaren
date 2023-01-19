# rakken/admin.py

# django
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# local
from .models import (
  Weer,
  Evenement,
  WaypointType,
  Waypoint,
  RakType,
  Rak,
  RakScore,
  Baan,
  )

# Register Weertype
class WeerAdmin(admin.ModelAdmin):
  list_display = ('windkracht', 'windrichting')
 
# overall admin area
admin.site.register(Weer, WeerAdmin)

# Register Evenementtype
class EvenementAdmin(admin.ModelAdmin):
  list_display = ('naam', 'beschrijving', 'datum')
  ordering     = ('datum', 'naam',)

# overall admin area
admin.site.register(Evenement, EvenementAdmin)

# Register Waypointtype
class WaypointTypeAdmin(admin.ModelAdmin):
  list_display = ('type', 'beschrijving',)
  ordering     = ('type',)

# overall admin area
admin.site.register(WaypointType, WaypointTypeAdmin)

# Register Waypoint
class WaypointAdmin(ImportExportModelAdmin):
  list_display  = ('naam', 'type', 'omschrijving', 'latitude', 'longitude',)
  list_per_page = 25
  ordering      = ('naam',)

# overall admin area
admin.site.register(Waypoint, WaypointAdmin)


# Register Raktype
class RakTypeAdmin(admin.ModelAdmin):
  list_display = ('type', 'beschrijving', 'max_aantal',)
  ordering     = ('type',)

# overall admin area
admin.site.register(RakType, RakTypeAdmin)


# Register Rak
class RakAdmin(ImportExportModelAdmin):
  list_display  = ('uuid', 'evenement', 'waypoint1', 'waypoint2', 'lengte', 'afstand', 'type',)
  ordering      = ('evenement', 'waypoint1',)
  list_filter   = ('evenement', 'type', 'waypoint1')
  list_per_page = 25

# overall admin area
admin.site.register(Rak, RakAdmin)


# Register RakScore
class RakScoreAdmin(admin.ModelAdmin):
  list_display = ('uuid', 'twa', 'score', )
  ordering     = ('uuid',)
 
# overall admin area
admin.site.register(RakScore, RakScoreAdmin)


# Register baan
class BaanAdmin(admin.ModelAdmin):
  list_display = ('naam', 'beschrijving',)
  ordering     = ('naam',)

# overall admin area
admin.site.register(Baan, BaanAdmin)
