import subprocess

import pandas as pd
import requests

from protzilla.constants.paths import RUNS_PATH, TEST_DATA_PATH


def create_graph(
    protein_id: str, peptide_df: pd.DataFrame, run_name: str, queue_size: int = None
):
    if not _protein_in_peptide_df(protein_id, peptide_df):
        raise ValueError(f"Protein {protein_id} not found in peptide_df.")

    path_to_protein_file = _get_protein_file(protein_id)
    cmd_str = f"protgraph -egraphml {path_to_protein_file} --export_output_folder={RUNS_PATH}/{run_name}/exported_graphs"
    subprocess.run(cmd_str, shell=True)

    return dict(
        graph_path=f"{RUNS_PATH}/{run_name}/exported_graphs/{protein_id}.graphml"
    )


def _get_protein_file(protein_id) -> str:
    protein_id = protein_id.upper()
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}.txt"
    r = requests.get(url)
    print(r.text)
    if r.status_code != 200:
        raise ValueError(f"Protein {protein_id} not found at UniprotKB.")
    elif not r.text:
        raise ValueError(f"Empty file returned for protein {protein_id}.")
    else:
        path_to_protein_file = f"{TEST_DATA_PATH}/proteins/{protein_id}.txt"
        with open(path_to_protein_file, "w") as f:
            f.write(r.text)

    return path_to_protein_file


def _protein_in_peptide_df(protein_id: str, peptide_df) -> bool:
    return protein_id in peptide_df.loc[:, "Protein ID"].unique().tolist()


if __name__ == "__main__":
    create_graph("F1SN00")
