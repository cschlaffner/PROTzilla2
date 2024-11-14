from typing import List

import pandas as pd
import plotly.graph_objects as go


def align_peptide_to_protein_sequence(
    peptide_sequence: str, protein_sequence: str
) -> List[int]:
    """
    Aligns a peptide to a protein sequence and returns the indices of the protein sequence where the peptide.
    NAIVE APPROACH
    """
    if (
        len(peptide_sequence) == 0
        or len(protein_sequence) == 0
        or len(peptide_sequence) > len(protein_sequence)
    ):
        return []
    indices = []
    for i in range(len(protein_sequence) - len(peptide_sequence) + 1):
        if protein_sequence[i : i + len(peptide_sequence)] == peptide_sequence:
            indices.append(i)
    return indices


def plot_protein_coverage(
    fasta_df: pd.DataFrame, peptide_df: pd.DataFrame, protein_id: str
) -> None:
    """
    Plots the coverage of a protein sequence by peptides.
    """
    # Retrieve the relevant peptides from the peptide df
    relevant_peptides = peptide_df[peptide_df["Protein ID"] == protein_id]
    protein_sequence = fasta_df[fasta_df["Protein ID"] == protein_id][
        "Protein Sequence"
    ].values[0]
    protein_sequence_length = len(protein_sequence)
    coverage = [0] * protein_sequence_length
    for peptide_sequence in relevant_peptides["Sequence"].unique():
        indices = align_peptide_to_protein_sequence(peptide_sequence, protein_sequence)
        for i in indices:
            for j in range(len(peptide_sequence)):
                coverage[i + j] += 1

    # Make sure coverage length matches the sequence length
    if len(coverage) != protein_sequence_length:
        raise ValueError("Length of coverage must match protein_sequence_length.")

    # Generate labels for amino acid positions
    amino_acid_positions = list(range(1, protein_sequence_length + 1))
    x_labels = [f"{i} ({protein_sequence[i - 1]})" for i in amino_acid_positions]

    # Create the bar chart
    fig = go.Figure()

    # Add bars for coverage values
    fig.add_trace(
        go.Bar(x=x_labels, y=coverage, name="Coverage", marker=dict(color="skyblue"))
    )

    # Customize layout
    fig.update_layout(
        title="Protein Coverage",
        xaxis_title="Amino Acid",
        yaxis_title="Coverage Value",
        xaxis=dict(tickmode="linear"),
        bargap=0.1,  # Adjust space between bars if needed
    )
    return dict(plots=[fig])
