"""
This module contains the code to parse a fasta file containing protein sequences and their ids.
"""
import logging

import pandas as pd
from Bio import SeqIO


def parse_fasta_id(fasta_id: str) -> str:
    """
    Parse the fasta id to get the protein name from the fasta id string
    """
    metadata = fasta_id.split("|")[1]
    if len(metadata) < 2:
        logging.warning(f"Metadata too short: {metadata}")
        return ""
    return metadata


def fasta_import(file_path: str) -> pd.DataFrame:
    """
    Import a fasta file and return a DataFrame with the protein sequences and their protein ids
    """
    fasta_iterator = SeqIO.parse(open(file_path), "fasta")
    protein_ids = []
    protein_sequences = []
    for fasta_sequence in fasta_iterator:
        id, sequence = parse_fasta_id(fasta_sequence.id), str(fasta_sequence.seq)
        protein_ids.append(id)
        protein_sequences.append(sequence)

    fasta_sequences = pd.DataFrame(
        {"Protein ID": protein_ids, "Protein Sequence": protein_sequences}
    )
    return {"fasta_df": fasta_sequences}
