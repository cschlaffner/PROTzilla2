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
    path("<str:run_name>/add", views.add, name="add"),
    path(
        "<str:run_name>/export_workflow", views.export_workflow, name="export_workflow"
    ),
    path("<str:run_name>/delete_step", views.delete_step, name="delete_step"),
    path("<str:run_name>/navigate", views.navigate, name="navigate"),
]
