from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from protzilla.run import Run

active_runs = {}


def index(request):
    """
    Renders the main index page of the PROTzilla application.

    :param request: the request object
    :type request: HttpRequest

    :return: the rendered index page
    :rtype: HttpResponse
    """
    return render(
        request,
        "runs_v2/index.html",
        context={
            "available_workflows": Run.available_workflows(),
            "available_runs": Run.available_runs(),
        },
    )


def create(request):
    """
    Creates a new run. The user is then redirected to the detail page of the run.

    :param request: the request object
    :type request: HttpRequest

    :return: the rendered details page of the new run
    :rtype: HttpResponse
    """
    run_name = request.POST["run_name"]
    run = Run.create(
        run_name,
        request.POST["workflow_config_name"],
        df_mode=request.POST["df_mode"],
    )
    active_runs[run_name] = run
    return HttpResponseRedirect(reverse("runs_v2:detail", args=(run_name,)))


def continue_(request):
    """
    Continues an existing run. The user is redirected to the detail page of the run and
    can resume working on the run.

    :param request: the request object
    :type request: HttpRequest

    :return: the rendered details page of the run
    :rtype: HttpResponse
    """
    run_name = request.POST["run_name"]
    active_runs[run_name] = Run.continue_existing(run_name)

    return HttpResponseRedirect(reverse("runs_v2:detail", args=(run_name,)))
