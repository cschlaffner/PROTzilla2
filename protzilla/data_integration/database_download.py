import requests
import shutil
import gzip
from pathlib import Path


def download_uniprot():
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
        with open("uniprot.tsv.gz", "wb") as f:
            shutil.copyfileobj(r.raw, f)

    with gzip.open("uniprot.tsv.gz", "rb") as g:
        with open("uniprot.tsv", "wb") as f:
            shutil.copyfileobj(g, f)

    Path("uniprot.tsv.gz").unlink()


if __name__ == "__main__":
    if not (Path(__file__).parent / "uniprot.tsv").exists():
        print("downloading Uniprot (about one minute)")
        download_uniprot()
        print("done downloading")
    else:
        print("Uniprot already downloaded")
