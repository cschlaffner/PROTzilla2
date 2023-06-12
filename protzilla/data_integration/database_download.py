import requests
from pathlib import Path
from requests.adapters import HTTPAdapter, Retry
import re
from tqdm import tqdm


database_path = Path(__file__).parent / "databases"


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


def download_uniprot_paged():
    retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retries))

    url = "https://rest.uniprot.org/uniprotkb/search?fields=accession,id,protein_name,gene_names,organism_name,length&format=tsv&query=%28organism_id:9606%29%20AND%20%28reviewed%3Atrue%29&size=500"
    progress = 0
    with open(database_path / "uniprot.tsv", "w") as f:
        for batch, total in get_batch(url, session):
            lines = batch.text.splitlines()
            if not progress:
                print(lines[0], file=f)
            for line in lines[1:]:
                print(line, file=f)
            progress += len(lines[1:])
            print(f"{progress} / {total}")


def download_uniprot_stream():
    with requests.get(
        "https://rest.uniprot.org/uniprotkb/stream",
        params=dict(
            format="tsv",
            query="(organism_id:9606)",
            fields="accession,id,protein_name,gene_primary,organism_name,length",
            compress="true",
        ),
        stream=True,
    ) as r:
        r.raise_for_status()
        with open(database_path / "uniprot.tsv", "wb") as f:
            for chunk in tqdm(r.iter_content(chunk_size=8192)):
                f.write(chunk)


if __name__ == "__main__":
    database_path.mkdir(exist_ok=True)
    if not (database_path / "uniprot.tsv").exists():
        print("downloading Uniprot (about one minute, 600 iterations)")
        try:
            download_uniprot_stream()
        except Exception as e:
            print(e)
            print("failed to download")
        else:
            print("done downloading")
    else:
        print("Uniprot already downloaded")
