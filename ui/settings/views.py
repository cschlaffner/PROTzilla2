import pandas

import plotly.io as pio
import plotly.graph_objects as go

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, NoReverseMatch
from django.template.loader import render_to_string

from protzilla.utilities.utilities import parameters_from_post
from protzilla.data_preprocessing.plots import create_bar_plot
from ui.settings.plot_template import template, load_settings, save_settings


SECTIONS = [
    {
        "id": "plots",
        "name": "Plot Configurations" 
    },
    {
        "id": "databases",
        "name": "Manage Databases"
    },
]


def make_sidebar(request, section_id):
    sidebar_template = "settings_sidebar.html"
    return render_to_string(
        sidebar_template,
        context=dict(
            sections=SECTIONS,
            selected_section=section_id
        )
    )


def settings_plots(request):
    settings_content = load_settings("plots")
    sidebar = make_sidebar(request, "plots")
    plot = make_preview_plot(settings_content)
    return render(
        request,
        "settings_plots.html",
        context=dict(
            initials=settings_content,
            sidebar=sidebar,
            plot=plot,
            sections=SECTIONS,
            section_id="plots"
        )
    )


def make_preview_plot(params: dict):
    template.update(params)
    fig = create_bar_plot(
        ["Example 1", "Example 2"],
        [0.7, 0.3],
        "Example plot",
        "Example",
        "Example"
    )
    pio.templates["plotly_protzilla_preview"] = go.layout.Template(layout=template.layout)
    fig.update_layout(template="plotly_protzilla_preview")
    plot = fig.to_html(include_plotlyjs=False, full_html=False)
    return plot


def update_plot_preview(request):
   params = parameters_from_post(request.POST)
   sidebar = make_sidebar(request, "plots")
   plot = make_preview_plot(params)
   return render(
       request,
        "settings_plots.html",
        context=dict(
            initials=params,
            sidebar=sidebar,
            plot=plot,
            section_id="plots"
        )
   ) 


def settings_databases(request):
    settings_content = load_settings("databases")
    sidebar = make_sidebar(request, "databases")
    return render(
        request,
        "settings_databases.html",
        context=dict(
            initials=settings_content,
            sidebar=sidebar,
            sections=SECTIONS,
            section_id="databases"
        )
    )


def save(request):
    params = parameters_from_post(request.POST)
    section_id = request.POST.get("section_id")
    save_settings(params, section_id)
    return HttpResponseRedirect(reverse("settings:last_view"))


def last_view(request):
    view_name = request.session['last_view']
    try:
        if view_name=="runs:detail":
            run_name = request.session['run_name']
            return HttpResponseRedirect(reverse(view_name, args=(run_name,)))
        else:
            return HttpResponseRedirect(reverse(view_name))
    except NoReverseMatch:
        return HttpResponseRedirect(reverse("runs:index"))