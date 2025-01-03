import pandas

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, NoReverseMatch
from django.template.loader import render_to_string

from protzilla.constants.paths import SETTINGS_PATH
from protzilla.disk_operator import YamlOperator
from protzilla.utilities.utilities import parameters_from_post
from ui.settings.user_settings_forms import ExportingPlotsSettingsForm


SECTIONS = [
    {
        "id": "general",
        "name": "General"
    },
    {
        "id": "plots",
        "name": "Exporting Plots" 
    }
]


def make_sidebar(request, section_id):
    template = "settings_sidebar.html"
    return render_to_string(
        template,
        context=dict(
            sections=SECTIONS,
            selected_section=section_id
        )
    )


def get_settings(section_id: str):
    op = YamlOperator()
    path = SETTINGS_PATH / (section_id + ".yaml")
    settings = op.read(path)
    return settings

def settings_general(request):
    settings_content = get_settings("general")
    settings_form = "" #TO DO: Add class GeneralSettingsForm
    sidebar = make_sidebar(request, "general")
    return render(
        request,
        "settings_general.html",
        context=dict(
            sidebar=sidebar,
            settings_form=settings_form,
            section_id="general"
        )
    )


def settings_plots(request):
    settings_content = get_settings("plots")
    settings_form = ExportingPlotsSettingsForm(initial=settings_content)
    sidebar = make_sidebar(request, "plots")
    return render(
        request,
        "settings_plots.html",
        context=dict(
            sidebar=sidebar,
            settings_form=settings_form,
            section_id="plots"
        )
    )


def save(request):
    params = parameters_from_post(request.POST)
    print(f"#####{params}")
    section_id = request.POST.get("section_id")
    op = YamlOperator()
    path = SETTINGS_PATH / (section_id + ".yaml")
    settings = op.write(path, params)
    # TO DO: Adjust current Plotly Template
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