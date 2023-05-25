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
    path("<str:run_name>/change_method", views.change_method, name="change_method"),
    path(
        "<str:run_name>/all_button_parameters",
        views.all_button_parameters,
        name="all_button_parameters",
    ),
    path("<str:run_name>/results_exist", views.results_exist, name="results_exist"),
    path("<str:run_name>/add_name", views.add_name, name="add_name"),
    path(
        "<str:run_name>/outputs_of_step", views.outputs_of_step, name="outputs_of_step"
    ),
    path(
        "<str:run_name>/change_field",
        views.change_field,
        name="change_field",
    ),
    path("<str:run_name>/add", views.add, name="add"),
    path("<str:run_name>/delete_step", views.delete_step, name="delete_step"),
    path(
        "<str:run_name>/export_workflow", views.export_workflow, name="export_workflow"
    ),
    path("<str:run_name>/download_plots", views.download_plots, name="download_plots"),
    path("<str:run_name>/tables/<int:index>", views.tables, name="tables"),
    path(
        "<str:run_name>/tables_content/<int:index>",
        views.tables_content,
        name="tables_content",
    ),
]
