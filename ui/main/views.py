from django.shortcuts import redirect, render
from protzilla.data_integration.database_query import uniprot_databases


def index(request):
    return redirect("/runs/")


def databases(request):
    return render(
        request,
        "databases.html",
        context=dict(uniprot_databases=uniprot_databases()),
    )
