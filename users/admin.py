# users/admin.py

# django
from django.contrib import admin

# local
from .models import UserProfile

# register userprofile model
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'created', 'country')