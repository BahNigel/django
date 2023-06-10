from django.contrib import admin

from .models import UserProfile,Blog

admin.site.register(UserProfile)

admin.site.register(Blog)