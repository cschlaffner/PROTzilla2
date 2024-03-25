from django.urls import path

from . import views

app_name = "runs_v2"
urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create, name="create"),
    path("continue", views.continue_, name="continue"),
]
