from protzilla.data_preprocessing.plots import create_pie_plot


def create_volcano_plot(intensity_df, a, b, **p):
    fig = create_pie_plot(
        values_of_sectors=[
            400,
            42,
        ],
        names_of_sectors=["Huiiiiiiii", "Flump"],
        heading="Wummmmmms",
    )
    print(intensity_df.head())
    print("------------------")
    print(a)
    print("------------------")
    print(p)

    return [fig]


# get_visualisation(
#     self,
#     intensity_df: pd.DataFrame,
#     pvalues_fc_df: pd.DataFrame,
#     corrected_alpha: float,
#     fc_threshold: float,
#     alpha: float = 0.05,
#     proteins_of_interest: "list[str]" = None,
#     y_title: str = "-log10(p)",
#     x_title: str = "log2(fc)",
#     heading: str = "Volcano plot",
# ) -> Figure:
#     """
#     A function to create a volcano plot of the t_test results. The plot
#     shows the -log10 of the corrected p-values on the y-axis and the
#     log2 fold change on the x-axis. A horizontal line is drawn at the
#     -log10 of the corrected alpha value. A vertical line is drawn at
#     the log2 fold change threshold.
#     The proteins that are differentially expressed are coloured in red and
#     the proteins that are not significant are coloured in blue.
#     :param intensity_df: the dataframe that should be tested in long format
#     :type intensity_df: pandas DataFrame
#     :param pvalues_fc_df: the dataframe that contains the corrected
#         p-values and the fold change
#     :type pvalues_fc_df: pandas DataFrame
#     :param corrected_alpha: the corrected alpha value
#     :type corrected_alpha: float or None
#     :param fc_threshold: the log2 fold change threshold
#     :type fc_threshold: float
#     :param alpha: the alpha value, defaults to 0.05
#     :type alpha: float
#     :param y_title: the y-axis title, defaults to ""
#     :type y_title: str
#     :param x_title: the x-axis title, defaults to ""
#     :type x_title: str
#     :param heading: the heading of the plot
#     :type heading: str
#     :return: a plotly Figure object
#     :rtype: Figure (plotly object)
#     """
#     pvalues_log2fc_df = pd.DataFrame(
#         {
#             "protein": intensity_df.loc[:, "Protein ID"].unique().tolist(),
#             "corrected_p_values": pvalues_fc_df["corrected_p_values"],
#             "log2_fold_change": np.log2(pvalues_fc_df["fold_change"]),
#         }
#     )
#     if corrected_alpha is None:
#         p_values_thresh = -np.log10(alpha)
#     else:
#         p_values_thresh = -np.log10(corrected_alpha)
#     fig = dashbio.VolcanoPlot(
#         dataframe=pvalues_log2fc_df,
#         effect_size="log2_fold_change",
#         p="corrected_p_values",
#         snp=None,
#         gene=None,
#         genomewideline_value=p_values_thresh,
#         effect_size_line=[-fc_threshold, fc_threshold],
#         xlabel=x_title,
#         ylabel=y_title,
#         title=heading,
#         annotation="protein",
#     )
#     if proteins_of_interest is None:
#         proteins_of_interest = []
#     # annotate the proteins of interest permanently in the plot
#     for protein in proteins_of_interest:
#         fig.add_annotation(
#             x=pvalues_log2fc_df.loc[
#                 pvalues_log2fc_df["protein"] == protein,
#                 "log2_fold_change",
#             ].values[0],
#             y=-np.log10(
#                 pvalues_log2fc_df.loc[
#                     pvalues_log2fc_df["protein"] == protein,
#                     "corrected_p_values",
#                 ].values[0]
#             ),
#             text=protein,
#             showarrow=True,
#             arrowhead=1,
#             font=dict(color="#ffffff"),
#             align="center",
#             arrowcolor="#4A536A",
#             bgcolor="#4A536A",
#             opacity=0.8,
#             ax=0,
#             ay=-20,
#         )
#     new_names = {
#         "Point(s) of interest": "Significant Proteins",
#         "Dataset": "Not Significant Proteins",
#     }
#     self.visualisation = fig.for_each_trace(
#         lambda t: t.update(
#             name=new_names[t.name],
#             legendgroup=new_names[t.name],
#         )
#     )
#     return self.visualisation
# def get_differentially_expressed_proteins(
#     self,
#     intensity_df: pd.DataFrame,
#     pvalues_fc_df: pd.DataFrame,
#     fc_threshold: float,
#     alpha: float = 0.05,
# ) -> pd.DataFrame:
#     """
#     A function to get the differentially expressed proteins. The proteins
#     are considered differentially expressed if the corrected p-value is
#     smaller than the p value threshold (alpha or corrected alpha)
#     and the positive log2 fold change is bigger than the log2 fold change
#     threshold.
#     :param intensity_df: the dataframe that should be filtered in long
#     format
#     :type intensity_df: pandas DataFrame
#     :param pvalues_fc_df: the dataframe that contains the corrected
#         p-values and the fold change
#     :type pvalues_fc_df: pandas DataFrame
#     :param fc_threshold: the log2 fold change threshold
#     :type fc_threshold: float
#     :param alpha: the alpha value, defaults to 0.05
#     :type alpha: float
#     :return: a dataframe with the differentially expressed proteins
#     :rtype: pandas DataFrame
#     """
#     pvalues_log2fc_df = pd.DataFrame(
#         {
#             "corrected_p_values": pvalues_fc_df["corrected_p_values"],
#             "log2_fold_change": np.log2(pvalues_fc_df["fold_change"]),
#         }
#     )
#     diff_exp_df = intensity_df["Protein ID"].to_frame()
#     diff_exp_df["p_values"] = pvalues_log2fc_df["corrected_p_values"]
#     diff_exp_df["fold_change"] = pvalues_log2fc_df["log2_fold_change"]
#     if self.corrected_alpha is None:
#         p_values_thresh = alpha
#     else:
#         p_values_thresh = self.corrected_alpha
#     self.differentially_expressed_proteins = diff_exp_df[
#         (diff_exp_df["p_values"] < p_values_thresh)
#         & (abs(diff_exp_df["fold_change"]) > fc_threshold)
#     ]
#     return self.differentially_expressed_proteins
