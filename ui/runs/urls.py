from django.urls import path

from . import views

app_name = "runs"
urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create, name="create"),
    path("continue", views.create, name="continue"),
    path("<str:run_name>", views.detail, name="detail"),
]
