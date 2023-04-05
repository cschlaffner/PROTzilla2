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
    path("<str:run_name>/change_method/", views.change_method, name="change_method"),
    path(
        "<str:run_name>/current_parameters/",
        views.current_parameters,
        name="current_parameters",
    ),
    path(
        "<str:run_name>/current_plot_parameters/",
        views.current_plot_parameters,
        name="current_plot_parameters",
    ),
    path("<str:run_name>/reults_exist/", views.results_exist, name="results_exist"),
    path(
        "<str:run_name>/plotted_for_params/",
        views.plotted_for_parameters,
        name="plotted_for_parameters",
    ),
]
