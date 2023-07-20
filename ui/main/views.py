import shutil
import pandas
import json
from datetime import date
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from protzilla.constants.paths import EXTERNAL_DATA_PATH
from protzilla.data_integration.database_query import uniprot_columns, uniprot_databases

database_metadata_path = EXTERNAL_DATA_PATH / "internal" / "metadata" / "uniprot.json"


def index(request):
    return redirect("/runs/")


def databases(request):
    databases = uniprot_databases()
    df_infos = {}
    if database_metadata_path.exists():
        with open(database_metadata_path, "r") as f:
            database_metadata = json.load(f)
    else:
        database_metadata = {}

    for db in databases:
        df_infos[db] = dict(
            cols=uniprot_columns(db),
            filesize=database_path(db).stat().st_size,
            date=database_metadata.get(db, {}).get("date", ""),
            num_proteins=database_metadata.get(db, {}).get("num_proteins", 0),
        )
    return render(
        request,
        "databases.html",
        context=dict(uniprot_databases=df_infos),
    )


def database_upload(request):
    name = request.POST["name"]
    if database_path(name).exists():
        msg = "Filename already taken."
        messages.add_message(request, messages.ERROR, msg, "alert-danger")
        return HttpResponseRedirect(reverse("databases"))

    path = dict(request.FILES)["new-db"][0].temporary_file_path()
    if not (EXTERNAL_DATA_PATH / "uniprot").exists():
        (EXTERNAL_DATA_PATH / "uniprot").mkdir(parents=True)

    just_copy = request.POST.get("just-copy", False)
    if just_copy:
        shutil.copy(path, database_path(name))
        num_proteins = 0
    else:
        if not path.endswith(".tsv"):
            msg = "File must be a tab-separated file with the extension .tsv"
            messages.add_message(request, messages.ERROR, msg, "alert-danger")
            return HttpResponseRedirect(reverse("databases"))

        try:
            dataframe = pandas.read_csv(path, sep="\t")
        except UnicodeDecodeError:
            msg = "File could not be decoded."
            messages.add_message(request, messages.ERROR, msg, "alert-danger")
            return HttpResponseRedirect(reverse("databases"))

        if "Entry" not in dataframe.columns:
            msg = "Required 'Entry' column not found."
            messages.add_message(request, messages.ERROR, msg, "alert-danger")
            return HttpResponseRedirect(reverse("databases"))

        dataframe.to_csv(database_path(name), sep="\t", index=False)
        num_proteins = len(dataframe)

    if not database_metadata_path.parent.exists():
        database_metadata_path.parent.mkdir(parents=True)

    if database_metadata_path.exists():
        with open(database_metadata_path, "r") as f:
            database_metadata = json.load(f)
    else:
        database_metadata = {}
    database_metadata[name] = dict(
        num_proteins=num_proteins, date=date.today().isoformat()
    )
    with open(database_metadata_path, "w") as f:
        json.dump(database_metadata, f)

    return HttpResponseRedirect(reverse("databases"))


def database_delete(request):
    database_name = request.POST["database"]
    path = database_path(database_name)
    path.unlink()

    if database_metadata_path.exists():
        with open(database_metadata_path, "r") as f:
            database_metadata = json.load(f)

        if database_name in database_metadata:
            del database_metadata[database_name]
            with open(database_metadata_path, "w") as f:
                json.dump(database_metadata, f)

    return HttpResponseRedirect(reverse("databases"))


def database_path(name):
    return EXTERNAL_DATA_PATH / "uniprot" / f"{name}.tsv"
