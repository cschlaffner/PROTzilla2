from django.shortcuts import redirect, render
from protzilla.data_integration.database_query import uniprot_databases, uniprot_columns
from django.http import HttpResponseRedirect
from django.urls import reverse
import pandas
from django.contrib import messages
from protzilla.constants.paths import EXTERNAL_DATA_PATH


def index(request):
    return redirect("/runs/")


def databases(request):
    databases = uniprot_databases()
    with_cols = {database: uniprot_columns(database) for database in databases}
    return render(
        request,
        "databases.html",
        context=dict(uniprot_databases=with_cols),
    )


def database_upload(request):
    # add option to copy and not verify the file?
    chosen_name = request.POST["name"]
    path = dict(request.FILES)["new-db"][0].temporary_file_path()
    try:
        dataframe = pandas.read_csv(path, sep="\t")
    except UnicodeDecodeError:
        messages.add_message(request, 40, "File could not be decoded.", "alert-danger")
        return HttpResponseRedirect(reverse("databases"))
    if "Entry" not in dataframe.columns:
        messages.add_message(
            request, 40, "Required 'Entry' column not found.", "alert-danger"
        )
        return HttpResponseRedirect(reverse("databases"))
    dataframe.to_csv(
        EXTERNAL_DATA_PATH / "uniprot" / f"{chosen_name}.tsv", sep="\t", index=False
    )
    return HttpResponseRedirect(reverse("databases"))
