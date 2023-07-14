import pandas
import json
from datetime import date
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from protzilla.constants.paths import EXTERNAL_DATA_PATH
from protzilla.data_integration.database_query import uniprot_columns, uniprot_databases

metadata_path = EXTERNAL_DATA_PATH / "internal" / "metadata" / "uniprot.json"


def index(request):
    return redirect("/runs/")


def databases(request):
    databases = uniprot_databases()
    df_infos = {}
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    else:
        metadata = {}

    for db in databases:
        df_infos[db] = dict(
            cols=uniprot_columns(db),
            filesize=database_path(db).stat().st_size,
            date=metadata.get(db, {}).get("date", ""),
            num_proteins=metadata.get(db, {}).get("num_proteins", 0),
        )
    return render(
        request,
        "databases.html",
        context=dict(uniprot_databases=df_infos),
    )


def database_upload(request):
    # add option to copy and not verify the file?
    chosen_name = request.POST["name"]
    # check for collision

    path = dict(request.FILES)["new-db"][0].temporary_file_path()
    if not path.endswith(".tsv") or path.endswith(".csv"):
        messages.add_message(
            request,
            messages.ERROR,
            "File must be a tab-separated file (.tsv, .csv).",
            "alert-danger",
        )
        return HttpResponseRedirect(reverse("databases"))
    try:
        dataframe = pandas.read_csv(path, sep="\t")
    except UnicodeDecodeError:
        messages.add_message(
            request, messages.ERROR, "File could not be decoded.", "alert-danger"
        )
        return HttpResponseRedirect(reverse("databases"))
    if "Entry" not in dataframe.columns:
        messages.add_message(
            request,
            messages.ERROR,
            "Required 'Entry' column not found.",
            "alert-danger",
        )
        return HttpResponseRedirect(reverse("databases"))
    if not (EXTERNAL_DATA_PATH / "uniprot").exists():
        (EXTERNAL_DATA_PATH / "uniprot").mkdir(parents=True)
    dataframe.to_csv(database_path(chosen_name), sep="\t", index=False)

    if not metadata_path.parent.exists():
        metadata_path.parent.mkdir(parents=True)

    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    else:
        metadata = {}
    metadata[chosen_name] = {
        "num_proteins": len(dataframe),
        "date": date.today().isoformat(),
    }
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)

    return HttpResponseRedirect(reverse("databases"))


def database_delete(request):
    database_name = request.POST["database"]
    path = database_path(database_name)
    path.unlink()
    return HttpResponseRedirect(reverse("databases"))


def database_path(name):
    return EXTERNAL_DATA_PATH / "uniprot" / f"{name}.tsv"
