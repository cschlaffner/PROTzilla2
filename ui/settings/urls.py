from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "settings"
urlpatterns = [
    path("general", views.settings_general, name="settings_general"),
    path("plots", views.settings_plots, name="settings_plots"),
]