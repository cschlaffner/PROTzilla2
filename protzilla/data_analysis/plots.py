import dash_bio as dashbio
import numpy as np


def create_volcano_plot(
    p_values, log2_fc, fc_threshold, alpha, proteins_of_interest=None
):
    plot_df = p_values.join(log2_fc.set_index("Protein ID"), on="Protein ID")
    fig = dashbio.VolcanoPlot(
        dataframe=plot_df,
        effect_size="log2_fold_change",
        p="corrected_p_value",
        snp=None,
        gene=None,
        genomewideline_value=alpha,
        effect_size_line=[-fc_threshold, fc_threshold],
        xlabel="log2(fc)",
        ylabel="-log10(p)",
        title="Volcano Plot",
        annotation="Protein ID",
    )

    if proteins_of_interest is None:
        proteins_of_interest = []

    # annotate the proteins of interest permanently in the plot
    for protein in proteins_of_interest:
        fig.add_annotation(
            x=plot_df.loc[
                plot_df["Protein ID"] == protein,
                "log2_fold_change",
            ].values[0],
            y=-np.log10(
                plot_df.loc[
                    plot_df["Protein ID"] == protein,
                    "corrected_p_value",
                ].values[0]
            ),
            text=protein,
            showarrow=True,
            arrowhead=1,
            font=dict(color="#ffffff"),
            align="center",
            arrowcolor="#4A536A",
            bgcolor="#4A536A",
            opacity=0.8,
            ax=0,
            ay=-20,
        )

    new_names = {
        "Point(s) of interest": "Significant Proteins",
        "Dataset": "Not Significant Proteins",
    }

    fig.for_each_trace(
        lambda t: t.update(
            name=new_names[t.name],
            legendgroup=new_names[t.name],
        )
    )

    return [fig]
