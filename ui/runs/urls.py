from django.urls import path

from . import views

app_name = "runs"
urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create, name="create"),
    path("continue", views.continue_, name="continue"),
    path("delete", views.delete_, name="delete"),
    path("detail/<str:run_name>", views.detail, name="detail"),
    path("<str:run_name>/plot", views.plot, name="plot"),
    path("<str:run_name>/tables/<int:index>", views.tables, name="tables_nokey"),
    path("<str:run_name>/tables/<int:index>/<str:key>", views.tables, name="tables"),
    path(
        "<str:run_name>/tables_content/<int:index>/<str:key>",
        views.tables_content,
        name="tables_content",
    ),
    path("<str:run_name>/next", views.next_, name="next"),
    path("<str:run_name>/back", views.back, name="back"),
    path("<str:run_name>/add", views.add, name="add"),
    path(
        "<str:run_name>/export_workflow", views.export_workflow, name="export_workflow"
    ),
    path("<str:run_name>/download_plots", views.download_plots, name="download_plots"),
    path("<str:run_name>/delete_step", views.delete_step, name="delete_step"),
    path("<str:run_name>/navigate", views.navigate, name="navigate"),
    path(
        "<str:run_name>/protein_graph/<int:index>",
        views.protein_graph,
        name="protein_graph",
    ),
    path("<str:run_name>/change_method", views.change_method, name="change_method"),
    path("<str:run_name>/add_name", views.add_name, name="add_name"),
    path("<str:run_name>/fill_form", views.fill_form, name="fill_form"),
    path(
        "<str:run_name>/download_table/<int:index>/<str:key>",
        views.download_table,
        name="download_table",
    ),
]
