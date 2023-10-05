import re
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter, Retry
from tqdm import tqdm
from datetime import date
import json

# cannot be imported form constants as package cannot be found
external_data_path = Path(__file__).parent.parent.parent / "user_data" / "external_data"
uniprot_db_path = external_data_path / "uniprot"
database_metadata_path = external_data_path / "internal" / "metadata" / "uniprot.json"


def get_next_link(headers):
    re_next_link = re.compile(r'<(.+)>; rel="next"')

    if "Link" in headers:
        match = re_next_link.match(headers["Link"])
        if match:
            return match.group(1)


def get_batch(batch_url, session):
    while batch_url:
        response = session.get(batch_url)
        response.raise_for_status()
        total = response.headers["x-total-results"]
        yield response, total
        batch_url = get_next_link(response.headers)


def download_uniprot_paged(name):
    """
    Downloads basic info on all human proteins from the uniprot paged rest api.
    this will take very long due to limitations in the api, therefore stream should be used.
    code taken from https://www.uniprot.org/help/api_queries including get_next_link and get_batch

    :param name: name the database will be saved as
    :type name: str
    """

    retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retries))

    url = "https://rest.uniprot.org/uniprotkb/search?fields=accession,id,protein_name,gene_names,organism_name,length&format=tsv&query=%28organism_id:9606%29%20AND%20%28reviewed%3Atrue%29&size=500"
    progress = 0
    with open(uniprot_db_path / f"{name}.tsv", "w") as f:
        for batch, total in get_batch(url, session):
            lines = batch.text.splitlines()
            if not progress:
                print(lines[0], file=f)
            for line in lines[1:]:
                print(line, file=f)
            progress += len(lines[1:])
            print(f"\rprogress: {progress} / {total}", end="")
        print()
    return total


def download_uniprot_stream(name):
    """
    Downloads basic info on all human proteins from the streamed uniprot rest api.
    can fail due to unstable internet connection or problems with the api.

    :param name: name the database will be saved as
    :type name: str
    """
    with requests.get(
        "https://rest.uniprot.org/uniprotkb/stream",
        params=dict(
            format="tsv",
            query="(organism_id:9606) AND (reviewed:true)",
            fields="accession,id,protein_name,gene_primary,organism_name,length",
            compress="true",
        ),
        stream=True,
    ) as r:
        r.raise_for_status()
        with open(uniprot_db_path / f"{name}.tsv", "wb") as f:
            for chunk in tqdm(r.iter_content(chunk_size=8192)):
                f.write(chunk)


if __name__ == "__main__":
    uniprot_db_path.mkdir(exist_ok=True, parents=True)
    database_metadata_path.parent.mkdir(exist_ok=True, parents=True)
    databases = [path for path in uniprot_db_path.iterdir() if path.suffix == ".tsv"]
    if databases:
        print(f"{len(databases)} Uniprot databases found, no download started")
    else:
        print("no Uniprot database found, starting to download")
        print("this will take 1-5 minutes")
        try:
            num_proteins = download_uniprot_paged("human_reviewed")
            infos = dict(num_proteins=num_proteins, date=date.today().isoformat())
            with open(database_metadata_path, "w") as f:
                json.dump(dict(human_reviewed=infos), f)
        except Exception as e:
            print(e)
            print(
                "\n\nfailed to download from UniProt, you can download it from "
                "\nhttps://www.uniprot.org/uniprotkb"
                "\nor from the protzilla release on github. "
                "\nfor more info go to the protzilla documentation on downloading UniProt"
            )
        else:
            print("done downloading")
