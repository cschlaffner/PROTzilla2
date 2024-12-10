import pandas
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, NoReverseMatch
from django.template.loader import render_to_string

from protzilla.constants.paths import EXTERNAL_DATA_PATH, SETTINGS_PATH
from protzilla.disk_operator import YamlOperator
from ui.settings.user_settings_forms import ExportingPlotsSettingsForm

user_settings_path = SETTINGS_PATH / "user_settings.yaml"


def make_sidebar(request, sections, section_id):
    template = "settings_sidebar.html"
    return render_to_string(
        template,
        context=dict(
            sections=sections,
            selected_section=section_id
        )
    )


def get_user_settings():
    op = YamlOperator()
    sections = op.read(user_settings_path)
    return sections


def settings_general(request):
    settings_form = ""
    sections = get_user_settings()
    sidebar = make_sidebar(request, sections, "general")
    return render(
        request,
        "settings_general.html",
        context=dict(
            sidebar=sidebar,
            settings_form=settings_form
        )
    )


def settings_plots(request):
    settings_form = ExportingPlotsSettingsForm
    sections = get_user_settings()
    sidebar = make_sidebar(request, sections, "plots")
    return render(
        request,
        "settings_plots.html",
        context=dict(
            sidebar=sidebar,
            settings_form=settings_form
        )
    )


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