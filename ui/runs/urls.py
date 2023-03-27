from django.urls import path

from . import views

app_name = "runs"
urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create, name="create"),
    path("continue", views.continue_, name="continue"),
    path("<str:run_name>", views.detail, name="detail"),
    path("<str:run_name>/calculate", views.calculate, name="calculate"),
    path("<str:run_name>/plot", views.plot, name="plot"),
    path("<str:run_name>/next", views.next_, name="next"),
    path("<str:run_name>/back", views.back, name="back"),
]
