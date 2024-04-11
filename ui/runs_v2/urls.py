from django.urls import path

from . import views

app_name = "runs_v2"
urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create, name="create"),
    path("continue", views.continue_, name="continue"),
    path("detail/<str:run_name>", views.detail, name="detail"),
    path("<str:run_name>/tables/<int:index>", views.tables, name="tables_nokey"),
    path("<str:run_name>/next", views.next_, name="next"),
    path("<str:run_name>/back", views.back, name="back"),
]
