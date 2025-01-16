from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "settings"
urlpatterns = [
    path("runs/", include("runs.urls")),
    path("general", views.settings_general, name="settings_general"),
    path("plots", views.settings_plots, name="settings_plots"),
    path("save", views.save, name="save"),
    path("last_view", views.last_view, name="last_view"),
    path("update_plot_preview", views.update_plot_preview, name="update_plot_preview")
]