from django.contrib import admin
from django.urls import include, path

urlpatterns = [path("", include("homevisit.urls")), path("admin/", admin.site.urls)]
