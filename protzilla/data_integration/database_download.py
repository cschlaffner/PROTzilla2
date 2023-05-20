import requests
import shutil
import gzip
from pathlib import Path
from requests.adapters import HTTPAdapter, Retry
import re


data_integration = Path(__file__).parent


def get_next_link(headers):
    re_next_link = re.compile(r'<(.+)>; rel="next"')

    if "Link" in headers:
        match = re_next_link.match(headers["Link"])
        if match:
            return match.group(1)


def get_batch(batch_url, session):
    while batch_url:
        print(batch_url)
        response = session.get(batch_url)
        response.raise_for_status()
        total = response.headers["x-total-results"]
        yield response, total
        batch_url = get_next_link(response.headers)


def download_uniprot_paged():
    retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retries))

    url = "https://rest.uniprot.org/uniprotkb/search?fields=accession,id,protein_name,gene_names,organism_name,length&format=tsv&query=%28organism_id:9606%29%20AND%20%28reviewed%3Atrue%29&size=500"
    progress = 0
    with open(data_integration / "uniprot.tsv", "w") as f:
        for batch, total in get_batch(url, session):
            lines = batch.text.splitlines()
            if not progress:
                print(lines[0], file=f)
            for line in lines[1:]:
                print(line, file=f)
            progress += len(lines[1:])
            print(f"{progress} / {total}")


def download_uniprot_stream():
    # takes a little more than a minute
    with requests.get(
        "https://rest.uniprot.org/uniprotkb/stream",
        params=dict(
            format="tsv",
            query="(organism_id:9606)",
            fields="accession,id,protein_name,gene_names,organism_name,length",
            compress="true",
        ),
        stream=True,
    ) as r:
        r.raise_for_status()
        with open(data_integration / "uniprot.tsv", "wb") as f:
            # shutil.copyfileobj(r.raw, f)
            for chunk in r.iter_content(chunk_size=8192):
                print(end=".")
                f.write(chunk)

    # with gzip.open(data_integration / "uniprot.tsv.gz", "rb") as g:
    #     with open(data_integration / "uniprot.tsv", "wb") as f:
    #         shutil.copyfileobj(g, f)

    # Path(data_integration / "uniprot.tsv.gz").unlink()


if __name__ == "__main__":
    if not (data_integration / "uniprot.tsv").exists():
        print("downloading Uniprot (about one minute)")
        download_uniprot_stream()
        print("done downloading")
    else:
        print("Uniprot already downloaded")
